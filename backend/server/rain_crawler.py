import json
import os.path
import time
import pytz
import requests as rq
from typing import Tuple, Union

from server.decode_meteo_rain import decode_geojson
from server.rain_db import RainDB
from server.config import ServerConfig
from server.mongo_db_api import MongoAPI, string_to_object_id, object_id_to_string
import server.mongo_db_common as mdbc
from server.mongodb_data_models import *

# ----------------------------------------------------------------------------------------------------------------------
# GLOBALS
# ----------------------------------------------------------------------------------------------------------------------
config_path = "/home/alisot2000/Documents/02_ETH/FWE/Weather-fusion/backend/data/server_config.json"


if not os.path.exists(config_path):
    raise FileNotFoundError("Please create the server_config.json file in the data folder")

with open(config_path, "r") as f:
    d = json.load(f)

    server_config = ServerConfig.model_validate(d)
    mongo = MongoAPI(db_address=server_config.mongo_db.address, db_name=server_config.mongo_db.database,
                     db_username=server_config.mongo_db.username, db_password=server_config.mongo_db.password)

# ----------------------------------------------------------------------------------------------------------------------
# Request Functions
# ----------------------------------------------------------------------------------------------------------------------


def request_radar_data(dt: datetime.datetime):
    """
    Request the radar data for a given datetime.
    """
    dts = dt.strftime("%Y%m%d_%H%M")
    rsp = rq.request("GET",
                     f"https://www.meteoschweiz.admin.ch/product/output/radar/rzc/radar_rzc.{dts}.json")

    if rsp.ok:
        return rsp.json()

    return None


def request_prediction_data(dt: datetime.datetime, version: datetime.datetime) -> Tuple[int, Union[dict, None]]:
    """
    Request the prediction data for a given datetime and provided a specific output version
    """
    dts = dt.strftime("%Y%m%d_%H%M")
    vss = version.strftime("%Y%m%d_%H%M")
    url = f"https://www.meteoschweiz.admin.ch/product/output/inca/precipitation/rate/version__{vss}/rate_{dts}.json"

    rsp = rq.request("GET", url)

    if rsp.ok:
        return rsp.status_code, rsp.json()

    return rsp.status_code, None


def init_db(db_path: str):
    """
    Init the database.
    """
    rdb = RainDB(db_path)
    rdb.create_tables()
    rdb.cleanup()


# Better idea https://www.meteoswiss.admin.ch/product/output/versions.json
# def get_next_prediction(dt: datetime.datetime):
#     """
#         Find the next prediction output if it exists, otherwise return the current one
#         """
#     # Get now and store the last version when we started
#     # Subtract 15min - for data movement on meteoswiss side
#     now = datetime.datetime.now() - datetime.timedelta(minutes=15)
#     last_version = dt
#
#     # Walk forward in time until we find the next production and next prediction
#     while dt < now:
#         next_prediction = dt - datetime.timedelta(minutes=dt.minute % 5) + datetime.timedelta(minutes=5)
#
#         st, js = request_prediction_data(next_prediction, dt)
#         if st == 200:
#             last_version = dt
#             print("Found new version", dt)
#
#         dt += datetime.timedelta(minutes=1)
#
#     return last_version


def get_next_prediction(dt: Union[datetime.datetime, None]):
    """
    Find the next prediction output if it exists, otherwise return the current one
    """
    # Get now and store the last version when we started
    # Subtract 15min - for data movement on meteoswiss side
    resp = rq.get("https://www.meteoswiss.admin.ch/product/output/versions.json")

    if resp.ok:
        content = resp.json()
        target_dt = content.get("inca/precipitation/rate")

        new_dt = pytz.utc.localize(datetime.datetime.strptime(target_dt, "%Y%m%d_%H%M"))
        if dt is None or new_dt > dt:
            return new_dt

    return dt


def update_prediction(version: datetime.datetime, update_time: datetime.datetime):
    """
    Update the prediction data
    """
    next_prediction = (update_time - datetime.timedelta(minutes=update_time.minute % 5,
                                                        seconds=update_time.second,
                                                        microseconds=update_time.microsecond)
                       + datetime.timedelta(minutes=5))

    # Get the prediction for as long as they come and insert into the database
    while True:
        assert next_prediction.minute % 5 == 0, "next_prediction is not a multiple of 5 minutes"
        st, js = request_prediction_data(next_prediction, version)

        # Successful request
        if st == 200:

            assert js is not None, "js is None from meteoswiss prediction response"
            store_path = os.path.join(server_config.data_home, "storage", "temp.json")

            print(f"Got Prediction: {next_prediction.strftime('%Y%m%d_%H%M')}")

            # Transform the MeteoData to GeoJSON
            transformed = decode_geojson(js)

            # Write to File
            with open(store_path, "w") as f:
                json.dump(transformed, f)

            record = RainRecord(
                dt=next_prediction,
                type="prediction",
                processed=True,
                version=version
            )

            record.record_id = mdbc.insert_prediction_record(mongo, record)

            os.rename(store_path, os.path.join(server_config.data_home, "storage",
                                               f"{object_id_to_string(record.record_id)}.json"))

        else:
            break

        next_prediction += datetime.timedelta(minutes=5)

    print("Done with prediction")


def crawl_prediction(update_time: datetime.datetime):
    """
    Crawl Radar Prediction.
    """
    old_prediction = mdbc.get_prediction_version(mongo)

    # check the next prediction
    new_version = get_next_prediction(old_prediction)

    # Update config if it has changed
    if old_prediction is None or new_version != old_prediction:
        update_prediction(version=new_version, update_time=update_time)


def crawl_radar(update_time: datetime.datetime):
    """
    Crawl the radar data.
    """
    latest_record = mdbc.get_latest_radar_record(mongo)
    latest_dt = latest_record.dt if latest_record is not None else datetime.datetime(update_time.year,
                                                                                     update_time.month,
                                                                                     update_time.day,
                                                                                     0, 0, 0,
                                                                                     tzinfo=datetime.UTC)

    assert type(latest_dt) is datetime.datetime, "type of last entry is not datetime"

    while latest_dt < update_time:
        assert latest_dt.minute % 5 == 0, "latest_dt is not a multiple of 5 minutes"

        data = request_radar_data(latest_dt)

        # only write if we have data
        if data is not None:
            transformed = decode_geojson(data)

            store_path = os.path.join(server_config.data_home, "storage",  f"temp.json")

            with open(store_path, "w") as f:
                json.dump(transformed, f)

            new_element = RainRecord(
                dt=latest_dt,
                type="radar",
                processed=True
            )

            record_id = mdbc.insert_radar_record(mongo, new_element)
            print("Got Radar for ", latest_dt)
            os.rename(store_path, os.path.join(server_config.data_home, "storage",
                                               f"{object_id_to_string(record_id)}.json"))

        latest_dt += datetime.timedelta(minutes=5)


if __name__ == "__main__":
    while True:
        update_dt = datetime.datetime.now()
        crawl_radar(update_time=update_dt)
        crawl_prediction(update_time=update_dt)
        print("Sleeping for 5 minutes")
        time.sleep(300)

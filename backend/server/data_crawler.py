import datetime
import json
import os.path
import time
import pytz
import requests as rq
from typing import Tuple, Union

from server.decode_meteo_rain import decode_geojson
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


def request_rain_prediction_data(dt: datetime.datetime, version: datetime.datetime) -> Tuple[int, Union[dict, None]]:
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


def request_wind_prediction_strength(dt: datetime.datetime,
                                     version: datetime.datetime,
                                     rt: RecordType) -> Tuple[int, Union[dict, None]]:
    """
    Request the prediction data for a given datetime and provided a specific output version
    """
    dts = dt.strftime("%Y%m%d_%H%M")
    vss = version.strftime("%Y%m%d_%H%M")
    if rt == RecordType.wind_10m:
        url = f"https://www.meteoschweiz.admin.ch/product/output/cosmo/wind-10m/images/version__{vss}/wind-10m_{dts}.json"
    elif rt == RecordType.wind_2000m:
        url = f"https://www.meteoschweiz.admin.ch/product/output/cosmo/wind-2000m/images/version__{vss}/wind-2000m_{dts}.json"
    else:
        raise ValueError("Unknown RecordType")

    rsp = rq.request("GET", url)
    if rsp.ok:
        return rsp.status_code, rsp.json()

    return rsp.status_code, None


def request_wind_direction_direction(dt: datetime.datetime,
                                     version: datetime.datetime,
                                     rt: RecordType) -> Tuple[int, Union[bytes, None]]:
    """
    Request the prediction data for a given datetime and provided a specific output version
    """
    dts = dt.strftime("%Y%m%d_%H%M")
    vss = version.strftime("%Y%m%d_%H%M")
    if rt == RecordType.wind_10m:
        url = f"https://www.meteoschweiz.admin.ch/product/output/cosmo/wind-10m/images/version__{vss}/wind-10m_{dts}.png"
    elif rt == RecordType.wind_2000m:
        url = f"https://www.meteoschweiz.admin.ch/product/output/cosmo/wind-2000m/images/version__{vss}/wind-2000m_{dts}.png"
    else:
        raise ValueError("Unknown RecordType")

    rsp = rq.request("GET", url)
    if rsp.ok:
        return rsp.status_code, rsp.content

    return rsp.status_code, None


def get_next_prediction(dt: Union[datetime.datetime, None], rt: RecordType):
    """
    Get next prediction
    """
    resp = rq.get("https://www.meteoswiss.admin.ch/product/output/versions.json")

    if resp.ok:
        content = resp.json()
        if rt == RecordType.rain:
            target_dt = content.get("inca/precipitation/rate")
        elif rt == RecordType.wind_10m:
            target_dt = content.get("cosmo/wind-10m/images")
        elif rt == RecordType.wind_2000m:
            target_dt = content.get("cosmo/wind-2000m/images")
        else:
            raise ValueError("Unknown RecordType")

        new_dt = pytz.utc.localize(datetime.datetime.strptime(target_dt, "%Y%m%d_%H%M"))
        if dt is None or new_dt > dt:
            return new_dt

    return dt


def update_rain_prediction(version: datetime.datetime, update_time: datetime.datetime):
    """
    Update the prediction data
    """
    next_prediction = (update_time - datetime.timedelta(minutes=update_time.minute % 5,
                                                        seconds=update_time.second,
                                                        microseconds=update_time.microsecond)
                       + datetime.timedelta(minutes=5))

    end_prediction = (update_time - datetime.timedelta(minutes=update_time.minute % 5,
                                                       seconds=update_time.second,
                                                       microseconds=update_time.microsecond)
                      + datetime.timedelta(days=2))

    # Get the prediction for as long as they come and insert into the database
    while next_prediction < end_prediction:
        assert next_prediction.minute % 5 == 0, "next_prediction is not a multiple of 5 minutes"
        st, js = request_rain_prediction_data(next_prediction, version)

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

            record.record_id = object_id_to_string(mdbc.insert_prediction_record(mongo, record))

            os.rename(store_path, os.path.join(server_config.data_home, "storage",
                                               f"{record.record_id}.json"))

        next_prediction += datetime.timedelta(minutes=5)

    print("Done with prediction")


def update_wind_10_prediction(version: datetime.datetime, update_time: datetime.datetime):
    """
    Update the prediction data for the wind at 10m height
    """
    next_prediction = (update_time - datetime.timedelta(minutes=update_time.minute,
                                                        seconds=update_time.second,
                                                        microseconds=update_time.microsecond)
                       + datetime.timedelta(hours=1))

    end_prediction = (update_time - datetime.timedelta(minutes=update_time.minute,
                                                       seconds=update_time.second,
                                                       microseconds=update_time.microsecond)
                      + datetime.timedelta(days=2))

    # Get the prediction for as long as they come and insert into the database
    while next_prediction < end_prediction:
        assert next_prediction.minute % 5 == 0, "next_prediction is not a multiple of 5 minutes"
        st, js = request_wind_prediction_strength(next_prediction, version, rt=RecordType.wind_10m)

        # Successful request
        if st == 200:
            assert js is not None, "js is None from meteoswiss prediction response"
            store_path = os.path.join(server_config.data_home, "storage", "temp.json")

            print(f"Got Prediction Strength 10m: {next_prediction.strftime('%Y%m%d_%H%M')}")

            # Transform the MeteoData to GeoJSON
            transformed = decode_geojson(js)

            # Write to File
            with open(store_path, "w") as f:
                json.dump(transformed, f)

            record = WindRecord(
                dt=next_prediction,
                type="strength",
                processed=True,
                version=version
            )

            record.record_id = object_id_to_string(mdbc.insert_wind_record(mongo, record))

            os.rename(store_path, os.path.join(server_config.data_home, "storage",
                                               f"{record.record_id}.json"))

        next_prediction += datetime.timedelta(hours=1)

    # Get the pngs.
    next_prediction = (update_time - datetime.timedelta(minutes=update_time.minute,
                                                        seconds=update_time.second,
                                                        microseconds=update_time.microsecond)
                       + datetime.timedelta(hours=1))

    # Get the prediction for as long as they come and insert into the database
    while next_prediction < end_prediction:
        assert next_prediction.minute % 5 == 0, "next_prediction is not a multiple of 5 minutes"
        st, img_data = request_wind_direction_direction(next_prediction, version, rt=RecordType.wind_10m)

        # Successful request
        if st == 200:
            assert img_data is not None, "js is None from meteoswiss prediction response"
            store_path = os.path.join(server_config.data_home, "storage", "temp.png")

            print(f"Got Prediction Direction 10m: {next_prediction.strftime('%Y%m%d_%H%M')}")

            # Write to File
            with open(store_path, "wb") as f:
                f.write(img_data)

            record = WindRecord(
                dt=next_prediction,
                type="direction",
                processed=True,
                version=version
            )

            record.record_id = object_id_to_string(mdbc.insert_wind_record(mongo, record))

            os.rename(store_path, os.path.join(server_config.data_home, "storage",
                                               f"{record.record_id}.png"))

        next_prediction += datetime.timedelta(hours=1)

    print("Done with prediction")


def crawl_rain_prediction(update_time: datetime.datetime):
    """
    Crawl Radar Prediction.
    """
    old_prediction = mdbc.get_rain_prediction_version(mongo)

    # check the next prediction
    new_version = get_next_prediction(old_prediction, RecordType.rain)

    # Update config if it has changed
    if old_prediction is None or new_version != old_prediction:
        update_rain_prediction(version=new_version, update_time=update_time)
        return True
    return False


def crawl_wind_prediction(update_time: datetime.datetime):
    """
    Crawl Wind Prediction.
    """
    old_prediction = mdbc.get_wind_prediction_version(mongo)

    # check the next prediction
    new_version = get_next_prediction(old_prediction, RecordType.wind_10m)

    # Update config if it has changed
    if old_prediction is None or new_version != old_prediction:
        update_wind_10_prediction(version=new_version, update_time=update_time)
        return True
    return False


def crawl_radar(update_time: datetime.datetime):
    """
    Crawl the radar data.
    """
    yesterday = update_time - datetime.timedelta(days=1)
    latest_record = mdbc.get_latest_radar_record(mongo)
    if latest_record is None:
        latest_dt = datetime.datetime(yesterday.year,
                                      yesterday.month,
                                      yesterday.day,
                                      0, 0, 0,
                                      tzinfo=datetime.UTC)
    else:
        latest_dt = pytz.utc.localize(latest_record.dt)

    assert type(latest_dt) is datetime.datetime, "type of last entry is not datetime"

    while latest_dt < update_time:
        assert latest_dt.minute % 5 == 0, "latest_dt is not a multiple of 5 minutes"

        data = request_radar_data(latest_dt)

        # only write if we have data
        if data is not None:
            transformed = decode_geojson(data)

            store_path = os.path.join(server_config.data_home, "storage", f"temp.json")

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


def regenerate_danger():
    pass


if __name__ == "__main__":
    while True:
        update_dt = datetime.datetime.now(datetime.UTC)
        crawl_radar(update_time=update_dt)
        data_changed = crawl_wind_prediction(update_time=update_dt)
        data_changed = data_changed or crawl_rain_prediction(update_time=update_dt)

        if data_changed:
            regenerate_danger()
        print("Sleeping for 5 minutes")
        time.sleep(300)

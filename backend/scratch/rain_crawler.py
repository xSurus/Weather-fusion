import datetime
import json
import os.path
import shutil
import time
import requests as rq
from typing import Tuple, Union

from server.decode_meteo_rain import decode_geojson
from server.rain_db import RainDB


# ----------------------------------------------------------------------------------------------------------------------
# GLOBALS
# ----------------------------------------------------------------------------------------------------------------------
data_home = "/home/alisot2000/Documents/02_ETH/FWE/Weather-fusion/backend/data"


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


def crawl_radar():
    """
    Crawl the radar data.
    """
    db_path = os.path.join(data_home, "rain.db")

    if not os.path.exists(db_path):
        init_db(db_path)

    rdb = RainDB(db_path)
    last_element = rdb.get_last_entry_radar()

    assert type(last_element) is datetime.datetime, "type of last entry is not datetime"

    now = datetime.datetime.now()

    while last_element < now:
        data = request_radar_data(last_element)

        # only write if we have data
        if data is not None:
            transformed = decode_geojson(data)

            with open(os.path.join(data_home, "history",  f"{last_element.strftime('%Y%m%d_%H%M')}.json"), "w") as f:
                json.dump(transformed, f)

            rdb.insert_radar_entry(last_element)
            print("Got Radar for ", last_element)

        last_element += datetime.timedelta(minutes=5)

    rdb.cleanup()


if __name__ == "__main__":
    while True:
        crawl_radar()
        print("Sleeping for 5 minutes")
        time.sleep(300)

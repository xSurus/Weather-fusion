import datetime
import json
import os.path
import time
import requests as rq

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


def init_db(db_path: str):
    rdb = RainDB(db_path)
    rdb.create_tables()
    rdb.cleanup()


def crawl_radar():
    data_home = "/home/alisot2000/Documents/02_ETH/FWE/Weather-fusion/backend/data"
    db_path = os.path.join(data_home, "rain.db")

    if not os.path.exists(db_path):
        init_db(db_path)

    rdb = RainDB(db_path)
    last_element = rdb.get_last_entry_radar()

    assert type(last_element) is datetime.datetime, "type of last entry is not datetime"

    now = datetime.datetime.now()

    while last_element < now:
        data = request_data(last_element)

        # only write if we have data
        if data is not None:
            transformed = decode_geojson(data)

            with open(os.path.join(data_home, f"{last_element.strftime('%Y%m%d_%H%M')}.json"), "w") as f:
                json.dump(transformed, f)

            rdb.insert_entry(last_element, "radar")
            print("Got Radar for ", last_element)

        last_element += datetime.timedelta(minutes=5)

    rdb.cleanup()


if __name__ == "__main__":
    while True:
        crawl_radar()
        print("Sleeping for 5 minutes")
        time.sleep(300)
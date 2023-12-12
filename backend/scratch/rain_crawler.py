import datetime
import json
import os.path
import time

import requests as rq

from server.rain_db import RainDB


def request_data(dt: datetime.datetime):
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
            with open(os.path.join(data_home, f"{last_element.strftime('%Y%m%d_%H%M')}.json"), "w") as f:
                json.dump(data, f)

            rdb.insert_entry(last_element, "radar")

        last_element += datetime.timedelta(minutes=5)

    rdb.cleanup()


if __name__ == "__main__":
    crawl_radar()
    time.sleep(60)
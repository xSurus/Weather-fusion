import datetime
import os
import json
import time
from typing import List

from server.mongo_db_api import *
import server.mongo_db_common as mdbc
from server.mongodb_data_models import *
from server.config import ServerConfig
from server.logs import setup_logging
import logging


# config_path = "/home/wf/weather_fusion/backend/data/server_config.json"
config_path = "/home/alisot2000/Documents/02_ETH/FWE/Weather-fusion/backend/data/server_config.json"

if not os.path.exists(config_path):
    raise FileNotFoundError("Please create the server_config.json file in the data folder")

with open(config_path, "r") as f:
    d = json.load(f)

    server_config = ServerConfig.model_validate(d)
    mongo = MongoAPI(db_address=server_config.mongo_db.address, db_name=server_config.mongo_db.database,
                     db_username=server_config.mongo_db.username, db_password=server_config.mongo_db.password)

# logging_cfg = "/home/wf/weather_fusion/backend/data/logging.yaml"
logging_cfg = "/home/alisot2000/Documents/02_ETH/FWE/Weather-fusion/backend/data/logging.yaml"
setup_logging(logging_cfg)


# ----------------------------------------------------------------------------------------------------------------------


def remove_rain(records: List[RainRecord], rain_type: str):
    """
    Remove the predictions from the records
    """
    fn_logger = logging.getLogger("db_prune_worker")

    db_count = 0
    file_count = 0

    for entry in records:
        p = os.path.join(server_config.data_home, "storage", f"{entry.record_id}.json")
        if os.path.exists(p):
            os.remove(p)
            file_count += 1

        db_count += mongo.delete_one(collection="rain_data", filter_dict={"_id": string_to_object_id(entry.record_id)})
    fn_logger.info(f"Deleted {db_count} {rain_type} entries from the database and {file_count} files from the storage")


def remove_wind(records: List[WindRecord]):
    db_count = 0
    file_count = 0

    fn_logger = logging.getLogger("db_prune_worker")

    for entry in records:
        if entry.type == WindRecordType.strength:
            p = os.path.join(server_config.data_home, "storage", f"{entry.record_id}.json")
        elif entry.type == WindRecordType.direction:
            p = os.path.join(server_config.data_home, "storage", f"{entry.record_id}.png")
        else:
            raise ValueError(f"Unknown wind record type: {entry.type}")

        if os.path.exists(p):
            os.remove(p)
            file_count += 1

        db_count += mongo.delete_one(collection="wind_data", filter_dict={"_id": string_to_object_id(entry.record_id)})
    fn_logger.info(f"Deleted {db_count} wind entries from the database and {file_count} files from the storage")


def remove_danger(records: List[WindRecord]):
    db_count = 0
    file_count = 0

    fn_logger = logging.getLogger("db_prune_worker")

    for entry in records:
        p = os.path.join(server_config.data_home, "storage", f"{entry.record_id}.json")

        if os.path.exists(p):
            os.remove(p)
            file_count += 1

        db_count += mongo.delete_one(collection="danger_data", filter_dict={"_id": string_to_object_id(entry.record_id)})
    fn_logger.info(f"Deleted {db_count} danger entries from the database and {file_count} files from the storage")


def prune_rain_prediction():
    """
    Get all the outdated predictions and delete them
    """
    entries = mdbc.get_outdated_rain_prediction_entries(mongo)

    remove_rain(entries, "rain prediction")


def prune_radar():
    """
    Prune the radar data. -> Radar files that are older than a day
    """
    now = datetime.datetime.now(datetime.UTC)
    entries = mdbc.get_outdated_radar_entries(mongo, now)
    remove_rain(entries, "rain radar")


def prune_danger():
    """
    Prune the danger data. -> Danger files that are older than a day
    """
    now = datetime.datetime.now(datetime.UTC)
    entries = mdbc.get_outdated_danger_records(mongo, now)
    remove_danger(entries)


def prune_wind():
    """
    Remove the data from the wind and danger collections that are older than 24 hours
    """
    now = datetime.datetime.now(datetime.UTC)
    entries = mdbc.get_outdated_wind_prediction_entries(mongo, now)
    remove_wind(entries)


if __name__ == "__main__":
    logger = logging.getLogger("db_prune_worker")

    while True:
        try:
            prune_radar()
        except Exception as e:
            logger.exception(f"Exception while pruning radar", e)

        try:
            prune_rain_prediction()
        except Exception as e:
            logger.exception(f"Exception while pruning rain prediction", e)

        try:
            prune_wind()
        except Exception as e:
            logger.exception(f"Exception while pruning wind prediction", e)

        try:
            prune_danger()
        except Exception as e:
            logger.exception(f"Exception while prudning danger map", e)
        time.sleep(300)


import os
import json
import time

from server.mongo_db_api import *
import server.mongo_db_common as mdbc
from server.mongodb_data_models import *
from server.config import ServerConfig


data_home = "/home/alisot2000/Documents/02_ETH/FWE/Weather-fusion/backend/data"
config_path = os.path.join(data_home, "server_config.json")

if not os.path.exists(config_path):
    raise FileNotFoundError("Please create the server_config.json file in the data folder")

with open(config_path, "r") as f:
    d = json.load(f)

    server_config = ServerConfig.model_validate(d)
    mongo = MongoAPI(db_address=server_config.mongo_db.address, db_name=server_config.mongo_db.database,
                     db_username=server_config.mongo_db.username, db_password=server_config.mongo_db.password)

# ----------------------------------------------------------------------------------------------------------------------


def remove_rain(records: List[RainRecord], rain_type: str):
    """
    Remove the predictions from the records
    """
    db_count = 0
    file_count = 0

    for entry in records:
        p = os.path.join(server_config.data_home, "storage", f"{entry.record_id}.json")
        if os.path.exists(p):
            os.remove(p)
            file_count += 1

        db_count += mongo.delete_one(collection="rain_data", filter_dict={"_id": string_to_object_id(entry.record_id)})
    print(f"Deleted {db_count} {rain_type} entries from the database and {file_count} files from the storage")


def prune_prediction():
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


if __name__ == "__main__":
    while True:
        prune_radar()
        prune_prediction()
        time.sleep(1800)

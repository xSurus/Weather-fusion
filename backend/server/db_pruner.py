import datetime
import os
import json

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
def prune_radar():
    """
    Prune the radar data. -> Radar files that are older than a day
    """
    now = datetime.datetime.now(datetime.UTC)
    entries = mdbc.get_outdated_radar_entries(mongo, now)
    # pytz.utc.localize(code_obj.expires)


if __name__ == "__main__":
    prune_radar()
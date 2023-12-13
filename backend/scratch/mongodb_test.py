from server.mongo_db_api import MongoAPI
from server.config import ServerConfig
import os
import json
import datetime
from server.mongodb_data_models import RainRecord, RecordType

data_home = "/home/alisot2000/Documents/02_ETH/FWE/Weather-fusion/backend/data"
config_path = os.path.join(data_home, "server_config.json")

if not os.path.exists(config_path):
    raise FileNotFoundError("Please create the server_config.json file in the data folder")

with open(config_path, "r") as f:
    d = json.load(f)

    server_config = ServerConfig.model_validate(d)
    mongo = MongoAPI(db_address=server_config.mongo_db.address, db_name=server_config.mongo_db.database,
                     db_username=server_config.mongo_db.username, db_password=server_config.mongo_db.password)

record = RainRecord(
    type="radar",
    dt=datetime.datetime.now(),
)
dtc = record.model_dump()
del dtc["record_id"]

mongo.insert_one(collection="rain_data", document_dict=dtc)
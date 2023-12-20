from server.mongo_db_api import MongoAPI, object_id_to_string
from server.config import ServerConfig
import os
import json
import datetime
from server.mongodb_data_models import RainRecord, RainRecordType

data_home = "/home/alisot2000/Documents/02_ETH/FWE/Weather-fusion/backend/data"
config_path = os.path.join(data_home, "server_config.json")

if not os.path.exists(config_path):
    raise FileNotFoundError("Please create the server_config.json file in the data folder")

with open(config_path, "r") as f:
    d = json.load(f)

    server_config = ServerConfig.model_validate(d)
    mongo = MongoAPI(db_address=server_config.mongo_db.address, db_name=server_config.mongo_db.database,
                     db_username=server_config.mongo_db.username, db_password=server_config.mongo_db.password)

all_data = mongo.find(collection="danger_data", filter_dict={})
print(len(all_data))
rm_count = 0
del_count = 0
for d in all_data:
    path = os.path.join(data_home, "storage", object_id_to_string(d['_id']) + ".json")
    if os.path.exists(path):
        os.remove(path)
        rm_count += 1

    del_count += mongo.delete_one(collection="danger_data", filter_dict={"_id": d['_id']})

print(f"Removed {rm_count} files and {del_count} database entries for danger_data")

all_data = mongo.find(collection="wind_data", filter_dict={})
print(len(all_data))
rm_count = 0
del_count = 0
for d in all_data:
    if d['type'] == "strength":
        path = os.path.join(data_home, "storage", object_id_to_string(d['_id']) + ".json")
    elif d['type'] == "direction":
        path = os.path.join(data_home, "storage", object_id_to_string(d['_id']) + ".png")
    else:
        print("Unknown type: ", d['type'])
        continue
    if os.path.exists(path):
        os.remove(path)
        rm_count += 1

    del_count += mongo.delete_one(collection="wind_data", filter_dict={"_id": d['_id']})

print(f"Removed {rm_count} files and {del_count} database entries for wind_data")

all_data = mongo.find(collection="rain_data", filter_dict={})
print(len(all_data))
rm_count = 0
del_count = 0
for d in all_data:
    path = os.path.join(data_home, "storage", object_id_to_string(d['_id']) + ".json")
    if os.path.exists(path):
        os.remove(path)
        rm_count += 1

    del_count += mongo.delete_one(collection="rain_data", filter_dict={"_id": d['_id']})

print(f"Removed {rm_count} files and {del_count} database entries for rain_data")

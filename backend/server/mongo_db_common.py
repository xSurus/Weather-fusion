import bson
from typing import Union, List

import pytz

from server.mongodb_data_models import *
from server.mongo_db_api import MongoAPI, string_to_object_id, object_id_to_string


def get_latest_radar_record(mongo: MongoAPI) -> Union[RainRecord, None]:
    """
    Get the latest radar record from the database.
    """
    res = mongo.find_one(collection="rain_data", filter_dict={"type": "radar"}, sort=[("dt", -1)])
    res["_id"] = object_id_to_string(res["_id"])
    if res is not None:
        return RainRecord(**res)

    return None


def get_prediction_version(mongo: MongoAPI) -> Union[RainRecord, None]:
    """
    Get the latest prediction version from the database.
    """
    res = mongo.find_one(collection="rain_data", filter_dict={"type": "prediction"}, sort=[("version", -1)])
    if res is not None:
        return pytz.utc.localize(res["version"])

    return None


def insert_radar_record(mongo: MongoAPI, record: RainRecord) -> bson.ObjectId:
    """
    Insert a radar record into the database.
    """
    dtc = record.model_dump()
    del dtc["record_id"]

    return mongo.insert_one(collection="rain_data", document_dict=dtc)


def get_outdated_radar_entries(mongo: MongoAPI, now: datetime.datetime) -> List[RainRecord]:
    """
    Get all outdated radar entries.
    """
    cutoff = now - datetime.timedelta(days=1)
    records = mongo.find(collection="rain_data", filter_dict={"$and": [{"type": "radar"}, {"dt": {"$lt": cutoff}}]})
    res = []

    for record in records:
        record["_id"] = object_id_to_string(record["_id"])
        res.append(RainRecord(**record))

    return res
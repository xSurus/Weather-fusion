import datetime
import bson
from typing import Union, List

import pytz

from server.mongodb_data_models import *
from server.mongo_db_api import MongoAPI, string_to_object_id, object_id_to_string


def get_latest_radar_record(mongo: MongoAPI) -> Union[RainRecord, None]:
    """
    Get the latest radar record from the database.
    """
    res = mongo.find_one(collection="rain_data", filter_dict={"type": "radar"}, sort={"dt": -1})
    res["_id"] = object_id_to_string(res["_id"])
    if res is not None:
        return RainRecord(**res)

    return None


def get_rain_prediction_version(mongo: MongoAPI) -> Union[datetime, None]:
    """
    Get the latest prediction version from the database.
    """
    res = mongo.find_one(collection="rain_data", filter_dict={"type": "prediction"}, sort={"version": -1})
    if res is not None:
        return pytz.utc.localize(res["version"])

    return None


def get_wind_prediction_version(mongo: MongoAPI) -> Union[datetime.datetime, None]:
    """
    Get the current version of the wind data
    """
    res = mongo.find_one(collection="wind_data", filter_dict={}, sort={"version": -1})
    if res is not None:
        return pytz.utc.localize(res["version"])

    return None


def insert_wind_record(mongo: MongoAPI, record: WindRecord) -> bson.objectid:
    """
    Insert a wind record into the database.
    """
    dtc = record.model_dump()
    del dtc["record_id"]

    return mongo.insert_one(collection="wind_data", document_dict=dtc)


def insert_radar_record(mongo: MongoAPI, record: RainRecord) -> bson.ObjectId:
    """
    Insert a radar record into the database.
    """
    dtc = record.model_dump()
    del dtc["record_id"]

    return mongo.insert_one(collection="rain_data", document_dict=dtc)


def insert_prediction_record(mongo: MongoAPI, record: RainRecord) -> bson.ObjectId:
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


def get_outdated_rain_prediction_entries(mongo: MongoAPI) -> List[RainRecord]:
    """
    Get all outdated prediction entries. (the ones who's version is no longer the newest)
    """
    newest_prediction = mongo.find_one(collection="rain_data", filter_dict={"type": "prediction"},
                                       sort={"version": -1})

    if newest_prediction is None:
        return []

    current_version = newest_prediction["version"]
    records = mongo.find(collection="rain_data", filter_dict={"$and": [{"type": "prediction"},
                                                                       {"version": {"$ne": current_version}}]})
    res = []
    for record in records:
        record["_id"] = object_id_to_string(record["_id"])
        res.append(RainRecord(**record))

    return res


def get_rain_record(mongo: MongoAPI, dt: datetime) -> Union[RainRecord, None]:
    """
    Get a rain record from the database.
    """

    assert dt.minute % 5 == 0, "dt is not a multiple of 5 minutes"

    res = mongo.find_one(collection="rain_data", filter_dict={
        "$or": [
            {
                "$and": [
                    {"type": "radar"},
                    {"dt": dt},
                ]
            },
            {
                "$and": [
                    {"type": "prediction"},
                    {"dt": dt},
                    {"version": {"$ne": None}},
                ]
            }
        ]
    },
                         sort={"version": -1})

    if res is not None:
        res["_id"] = object_id_to_string(res["_id"])
        return RainRecord(**res)

    return None

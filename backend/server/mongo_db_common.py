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
    if res is not None:
        res["_id"] = object_id_to_string(res["_id"])
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


def get_outdated_wind_prediction_entries(mongo: MongoAPI, now) -> List[WindRecord]:
    """
    Get the outdated wind records and return them (only based on the datetime of the record - not version)
    """
    # TODO can be improved to only retain one entry per time. (only the newest version)
    records = mongo.find(collection="wind_data", filter_dict={"dt": {"$lt": now}})

    res = []
    for record in records:
        record["_id"] = object_id_to_string(record["_id"])
        res.append(WindRecord(**record))

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


def get_wind_speed(mongo: MongoAPI, dt: datetime):
    """
    Get the wind speed record from the database.
    """
    assert dt.minute == 0, "dt is not a multiple of 5 minutes"
    res = mongo.find_one(collection="wind_data", filter_dict={"$and": [{"type": "strength"}, {"dt": dt}]},
                         sort={"version": -1})

    if res is not None:
        res["_id"] = object_id_to_string(res["_id"])
        return WindRecord(**res)

    return None


def get_wind_direction(mongo: MongoAPI, dt: datetime):
    """
    Get the wind direction record from the database.
    """
    assert dt.minute == 0, "dt is not a multiple of 5 minutes"
    res = mongo.find_one(collection="wind_data", filter_dict={"$and": [{"type": "direction"}, {"dt": dt}]},
                         sort={"version": -1})

    if res is not None:
        res["_id"] = object_id_to_string(res["_id"])
        return WindRecord(**res)

    return None


def get_all_wind_records_of_version(mongo: MongoAPI, version: datetime.datetime, wt: WindRecordType) -> List[WindRecord]:
    """
    Get all wind records of a specific version.

    :param mongo: Mongodb to use
    :param version: Version to get
    :param wt: Wind record type (so either strength or direction)
    """
    records = mongo.find(collection="wind_data", filter_dict={"$and": [{"version": version}, {"type": wt}]})

    res = []
    for record in records:
        record["_id"] = object_id_to_string(record["_id"])
        res.append(WindRecord(**record))

    return res


def insert_danger_record(mongo: MongoAPI, record: DangerRecord) -> bson.ObjectId:
    """
    Insert a danger record into the database.
    """
    dtc = record.model_dump()
    del dtc["record_id"]
    dtc["rain_id"] = string_to_object_id(dtc["rain_id"])
    dtc["wind_id"] = string_to_object_id(dtc["wind_id"])

    return mongo.insert_one(collection="danger_data", document_dict=dtc)


def get_danger_record(mongo: MongoAPI, dt: datetime.datetime) -> Union[DangerRecord, None]:
    """
    Get a danger record from the database.
    """
    assert dt.minute % 5 == 0, "dt is not a multiple of 5 minutes"

    res = mongo.find_one(collection="danger_data", filter_dict={"dt": dt}, sort=[("rain_version", -1), ("wind_version", -1)])

    if res is not None:
        res["_id"] = object_id_to_string(res["_id"])
        res["rain_id"] = object_id_to_string(res["rain_id"])
        res["wind_id"] = object_id_to_string(res["wind_id"])
        return DangerRecord(**res)

    return None


def get_outdated_danger_records(mongo: MongoAPI, now: datetime.datetime):
    """
    Get all outdated danger records.
    """
    # TODO can be improved to only retain one entry per time. (only the newest version)
    records = mongo.find(collection="danger_data", filter_dict={"dt": {"$lt": now}})

    res = []
    for record in records:
        record["_id"] = object_id_to_string(record["_id"])
        record["rain_id"] = object_id_to_string(record["rain_id"])
        record["wind_id"] = object_id_to_string(record["wind_id"])
        res.append(DangerRecord(**record))

    return res

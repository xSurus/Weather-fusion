import json
import os
import datetime
import warnings

import pytz
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from server.config import ServerConfig

import server.mongo_db_common as mdbc
from server.mongo_db_api import MongoAPI, string_to_object_id, object_id_to_string


# config_path = "/home/alisot2000/Documents/02_ETH/FWE/Weather-fusion/backend/data/server_config.json"
config_path = "/home/wf/weather_fusion/backend/data/server_config.json"


app = FastAPI(title="Weather Fusion", version="0.1.0", docs_url=None, redoc_url=None)
api_app = FastAPI(title="Weather Fusion API", version="0.1.0", docs_url=None, redoc_url=None)


if not os.path.exists(config_path):
    raise FileNotFoundError("Please create the server_config.json file in the data folder")

with open(config_path, "r") as f:
    d = json.load(f)

    server_config = ServerConfig.model_validate(d)

    mongo = MongoAPI(db_address=server_config.mongo_db.address, db_name=server_config.mongo_db.database,
                     db_username=server_config.mongo_db.username, db_password=server_config.mongo_db.password)


# ----------------------------------------------------------------------------------------------------------------------
# Static File Serving
# ----------------------------------------------------------------------------------------------------------------------


def gen_dt(five_minutes: int):
    now = datetime.datetime.now(datetime.timezone.utc)
    now -= datetime.timedelta(minutes=now.minute % 5, seconds=now.second, microseconds=now.microsecond)
    return now + datetime.timedelta(minutes=five_minutes*5)


@api_app.get("/get-rain-data")
def get_rain(five_minutes: int):
    """
    Get the rain data for a specific date
    """
    dt = gen_dt(five_minutes)
    if dt.minute % 5 != 0:
        raise HTTPException(status_code=400, detail="Date must be a multiple of 5 minutes")

    # check if it exists in the radar data:
    record = mdbc.get_rain_record(mongo, dt)
    if record is None:
        raise HTTPException(404, "Record not found")
    path = os.path.join(server_config.data_home, "storage", f"{record.record_id}.json")

    if os.path.exists(path):
        return FileResponse(path)

    raise HTTPException(status_code=500, detail="Data not found")


@api_app.get("/get-wind-speed")
def get_wind_speed(five_minutes: int):
    """
    Get the wind speed json from the database with the newest date.
    """
    dt = gen_dt(five_minutes)
    if dt.minute != 0 or dt.second != 0:
        raise HTTPException(status_code=400, detail="Wind only available hourly.")

    # check if it exists in the radar data:
    record = mdbc.get_wind_speed(mongo, dt)
    if record is None:
        raise HTTPException(404, "Record not found")

    path = os.path.join(server_config.data_home, "storage", f"{record.record_id}.json")

    if os.path.exists(path):
        return FileResponse(path)

    raise HTTPException(status_code=500, detail="Data not found")


@api_app.get("/get-wind-direction")
def get_wind_direction(five_minutes: int):
    """
    Get the wind direction png from the database with the newest date.
    """
    dt = gen_dt(five_minutes)
    if dt.minute != 0 or dt.second != 0:
        raise HTTPException(status_code=400, detail="Wind only available hourly.")

    # check if it exists in the radar data:
    record = mdbc.get_wind_direction(mongo, dt)
    if record is None:
        raise HTTPException(404, "Record not found")

    path = os.path.join(server_config.data_home, "storage", f"{record.record_id}.png")

    if os.path.exists(path):
        warnings.warn("Sending png file - will switch to geojson soon")
        return FileResponse(path)

    raise HTTPException(status_code=500, detail="Data not found")


@api_app.get("/get-danger-noodle")
def get_danger_noodle(five_minutes: int):
    """
    Get the danger areas for the given date.
    """
    dt = gen_dt(five_minutes)
    if dt.minute % 5 != 0:
        raise HTTPException(status_code=400, detail="danger is available every 5 min")

    # check if it exists in the radar data:
    record = mdbc.get_danger_record(mongo, dt)
    if record is None:
        raise HTTPException(404, "Record not found")

    path = os.path.join(server_config.data_home, "storage", f"{record.record_id}.json")

    if os.path.exists(path):
        return FileResponse(path)

    raise HTTPException(status_code=500, detail="Data not found")


main = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "webinterface",
                    "dist")
assets = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "webinterface",
                      "dist", "assets")


@api_app.get("/test-error")
def test_error():
    raise ValueError("Some Value Error for testing")


app.mount("/assets", StaticFiles(directory=assets), name="assets")
app.mount("/api-v1", api_app, name="api-v1")


@app.get("/{full_path:path}")
async def serve_main(full_path: str):
    abs_path = os.path.abspath(os.path.join(main, full_path))
    top = abs_path[:len(main)]
    if top != main:
        raise HTTPException(status_code=404, detail="File not found")

    if os.path.isfile(abs_path):
        return FileResponse(abs_path)
    return FileResponse(os.path.join(main, "index.html"))


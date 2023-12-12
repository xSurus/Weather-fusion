import os
import datetime

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse


storage_path = "/home/alisot2000/Documents/02_ETH/FWE/Weather-fusion/backend/data"


app = FastAPI(title="Weather Fusion", version="0.1.0")
api_app = FastAPI(title="Weather Fusion API", version="0.1.0")


# ----------------------------------------------------------------------------------------------------------------------
# Static File Serving
# ----------------------------------------------------------------------------------------------------------------------


@api_app.get("/get-rain-data")
def get_rain(date: str):
    """
    Get the rain data for a specific date

    Send date in formtat YYYY-MM-DD HH:MM
    """
    dt = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
    if dt.minute % 5 != 0:
        raise HTTPException(status_code=400, detail="Date must be a multiple of 5 minutes")

    # check if it exists in the radar data:
    file_name = f"{dt.strftime('%Y%m%d_%H%M')}.json"
    history_path = os.path.join(storage_path, "history", file_name)
    prediction_path = os.path.join(storage_path, "prediction", file_name)

    if os.path.exists(history_path):
        return FileResponse(history_path)

    elif os.path.exists(prediction_path):
        return FileResponse(os.path.join(storage_path, "prediction", file_name))

    raise HTTPException(status_code=404, detail="No data for this date")


main = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "webinterface",
                    "dist")
assets = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "webinterface",
                      "dist", "assets")
app.mount("/assets", StaticFiles(directory=assets), name="assets")
app.mount("/api-v1", api_app, name="api-v1")


@app.get("/{full_path:path}")
async def serve_main(full_path: str):
    return FileResponse(os.path.join(main, "index.html"))


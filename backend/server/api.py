import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse


app = FastAPI(title="Weather Fusion", version="0.1.0")
api_app = FastAPI(title="Weather Fusion API", version="0.1.0")


# ----------------------------------------------------------------------------------------------------------------------
# Static File Serving
# ----------------------------------------------------------------------------------------------------------------------


main = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "webinterface",
                    "dist")
assets = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "webinterface",
                      "dist", "assets")
app.mount("/assets", StaticFiles(directory=assets), name="assets")
app.mount("/api-v1", api_app, name="api-v1")


@app.get("/{full_path:path}")
async def serve_main(full_path: str):
    return FileResponse(os.path.join(main, "index.html"))


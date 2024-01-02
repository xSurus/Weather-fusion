import uvicorn
from server.api import app
import os

logging_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "logging.yaml")
uvicorn.run(app, host="localhost", port=8000, log_config=logging_config)

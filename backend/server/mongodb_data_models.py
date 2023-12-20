from pydantic import BaseModel, Field
import datetime
from typing import Union
from enum import Enum


class RecordType(str, Enum):
    rain = "rain"
    wind_10m = "wind-10m"
    wind_2000m = "wind-2000m"


class RainRecordType(str, Enum):
    radar = "radar"
    prediction = "prediction"


class WindRecordType(str, Enum):
    strength = "strength"
    direction = "direction"


class RainRecord(BaseModel):
    record_id: Union[None, str] = Field(alias='_id', default=None)
    dt: datetime.datetime
    type: RainRecordType
    version: Union[None, datetime.datetime] = None
    processed: bool = False


class WindRecord(BaseModel):
    record_id: Union[None, str] = Field(alias='_id', default=None)
    dt: datetime.datetime
    type: WindRecordType
    version: Union[None, datetime.datetime] = None
    processed: bool = False


class DangerRecord(BaseModel):
    record_id: Union[None, str] = Field(alias='_id', default=None)
    dt: datetime.datetime
    wind_id: str = None
    rain_id: str = None
    wind_version: Union[None, datetime.datetime] = None
    rain_version: Union[None, datetime.datetime] = None

from pydantic import BaseModel, Field
import datetime
from typing import Union
from enum import Enum


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

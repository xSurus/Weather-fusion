from pydantic import BaseModel


class MongoDBAccess(BaseModel):
    username: str
    password: str
    address: str
    database: str


class ServerConfig(BaseModel):
    mongo_db: MongoDBAccess

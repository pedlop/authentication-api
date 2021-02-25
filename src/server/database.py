import motor.motor_asyncio
from decouple import config

MONGO_DETAILS = config("MONGO_DETAILS")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client["authentication-sandbox"]

users_collection = database.get_collection("users")
users_collection.create_index("username", unique=True)
users_collection.create_index("email", unique=True)

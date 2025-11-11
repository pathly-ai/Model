# db.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = MongoClient(MONGO_URI)
db = client["pathly"]
# Define your collections
users_collection = db["users"]
assessments_collection = db["assessments"]
chats_collection = db["chats"]

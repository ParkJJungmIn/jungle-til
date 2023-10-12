from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
client = MongoClient( DB_HOST, 27017)

def get_db():
    return client.jungle7

def get_secret_key():
    return "JUNGLE"

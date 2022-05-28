from pymongo import MongoClient
import pymongo
import os
import certifi
import secrets

connection_str = secrets.db_connection

def get_database():
    global connection_str
    client = MongoClient(connection_str, tlsCAFile=certifi.where())
    return client['discord_bot']
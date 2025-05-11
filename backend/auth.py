from pymongo import MongoClient
from bson.objectid import ObjectId

# MongoDB setup
client = MongoClient("your_connection_string_here")
db = client['BankingAppDB']
users_collection = db['users']

def register_user(name, email, password):
    if users_collection.find_one({"email": email}):
        return {"success": False, "message": "User already exists."}

    new_user = {"name": name, "email": email, "password": password}
    users_collection.insert_one(new_user)
    return {"success": True, "message": "User registered successfully."}

def login_user(email, password):
    user = users_collection.find_one({"email": email, "password": password})
    if user:
        return {"success": True, "message": "Login successful."}
    return {"success": False, "message": "Invalid credentials."}

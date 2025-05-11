from pymongo import MongoClient

# MongoDB connection string
client = MongoClient("mongodb+srv://banking_user:Mpendulo00@bankingappdb.4zq89p5.mongodb.net/?retryWrites=true&w=majority")

# Define the database
db = client.get_database("banking_app")

# Define the user collection
users_collection = db.get_collection("users")

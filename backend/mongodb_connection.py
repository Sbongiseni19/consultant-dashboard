from pymongo import MongoClient

# Replace the connection string below with your actual string
connection_string = "mongodb+srv://banking_user:Mpendulo00%40@bankingappdb.4zq89p5.mongodb.net/BankingAppDB?retryWrites=true&w=majority"

# Connect to the MongoDB server
client = MongoClient(connection_string)

# Get the database
db = client['BankingAppDB']  # You can replace 'BankingAppDB' with your actual DB name

# Now you can interact with your collections (tables in SQL) within the database
# Example: Access a collection named "users"
users_collection = db['users']

# Insert a new user (as an example)
new_user = {"name": "John Doe", "email": "johndoe@example.com", "password": "securepassword"}
users_collection.insert_one(new_user)

# Querying for all users
for user in users_collection.find():
    print(user)

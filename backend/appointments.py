from pymongo import MongoClient
from datetime import datetime

# MongoDB setup
client = MongoClient("your_connection_string_here")
db = client['BankingAppDB']
appointments_collection = db['appointments']

def book_appointment(user_email, service_type, appointment_date):
    appointment = {
        "email": user_email,
        "service": service_type,
        "date": appointment_date,
        "booked_at": datetime.utcnow()
    }
    appointments_collection.insert_one(appointment)
    return {"success": True, "message": "Appointment booked successfully."}

import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from fastapi import FastAPI
from datetime import datetime

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware right after app is created
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can later restrict this to 'http://localhost:5500' or your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File paths
USER_DATA_FILE = "users.json"
BOOKING_DATA_FILE = "bookings.json"

# Models
class User(BaseModel):
    name: str
    email: str
    password: str

class LoginData(BaseModel):
    email: str
    password: str

class Booking(BaseModel):
    name: str
    id_number: str
    email: str
    selected_bank: str
    selected_service: str

class BookingWithId(Booking):
    id: str
    booking_time: str

# In-memory storage
bookings = []
users = []

def load_data():
    global bookings, users
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE) as f:
            try:
                users = json.load(f)
            except:
                users = []
    if os.path.exists(BOOKING_DATA_FILE):
        with open(BOOKING_DATA_FILE) as f:
            try:
                bookings = json.load(f)
            except:
                bookings = []

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from Heroku!"}

def save_data():
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f)
    with open(BOOKING_DATA_FILE, 'w') as f:
        json.dump(bookings, f)

@app.post("/register")
async def register_user(user: User):
    for u in users:
        if u['email'] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    users.append(user.dict())
    save_data()
    return {"message": "User registered successfully"}

@app.post("/login")
async def login_user(login_data: LoginData):
    if login_data.email == "admin@gmail.com" and login_data.password == "123":
        return {"message": "Admin login successful", "role": "admin"}

    for u in users:
        if u['email'] == login_data.email and u['password'] == login_data.password:
            return {"message": "User login successful", "role": "user", "name": u['name'], "email": u['email']}
    raise HTTPException(status_code=401, detail="Invalid email or password")

@app.post("/book", response_model=BookingWithId)
async def book_slot(booking: Booking):
    booking_id = str(uuid4())
    booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_booking = BookingWithId(id=booking_id, booking_time=booking_time, **booking.dict())
    bookings.append(new_booking.dict())
    save_data()
    return new_booking

@app.get("/bookings", response_model=list[BookingWithId])
async def get_bookings():
    return bookings

@app.delete("/bookings/{booking_id}", response_model=BookingWithId)
async def delete_booking(booking_id: str):
    global bookings
    booking = next((b for b in bookings if b['id'] == booking_id), None)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    bookings = [b for b in bookings if b['id'] != booking_id]
    save_data()
    return booking

# Load data when app starts
load_data()

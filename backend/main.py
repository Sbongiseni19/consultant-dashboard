import json
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates and static file directories
templates = Jinja2Templates(directory="templates")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")  # Proper static file serving

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

# Load data from JSON files
def load_data():
    global bookings, users
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE) as f:
                users = json.load(f)
        except json.JSONDecodeError:
            users = []
    if os.path.exists(BOOKING_DATA_FILE):
        try:
            with open(BOOKING_DATA_FILE) as f:
                bookings = json.load(f)
        except json.JSONDecodeError:
            bookings = []

# Save data to JSON files
def save_data():
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    with open(BOOKING_DATA_FILE, 'w') as f:
        json.dump(bookings, f, indent=2)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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

# Load existing data
load_data()

# Run the app if this file is the main program
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

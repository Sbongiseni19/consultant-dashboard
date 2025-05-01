import json
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
import uvicorn
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates directory
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.route('/assets/<path:path>')
def serve_assets(path):
    return send_from_directory('assets', path)

def save_data():
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f)
    with open(BOOKING_DATA_FILE, 'w') as f:
        json.dump(bookings, f)

# Add these new endpoints to your existing FastAPI app

@app.post("/login")
async def login_user(login_data: LoginData):
    user = next((u for u in users if u['email'] == login_data.email), None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user['password'] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Login successful", "user": user}

@app.post("/register")
async def register_user(user: User):
    if any(u['email'] == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")
    users.append(user.dict())
    save_data()
    return {"message": "Registration successful", "user": user}



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

# Load data at startup
load_data()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
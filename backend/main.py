import json
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
import uvicorn
from pymongo import MongoClient

# Initialize FastAPI app
app = FastAPI()

# MongoDB Atlas connection
connection_string = "mongodb+srv://banking_user:Mpendulo00@bankingappdb.4zq89p5.mongodb.net/?retryWrites=true&w=majority&appName=BankingAppDB"

# Connect to the MongoDB Atlas cluster
client = MongoClient(connection_string)
db = client["bankingappdb"]  # Replace with your database name
collection = db["users"]  # Example collection

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

# In-memory storage (removed since we're using MongoDB)
# bookings = []
# users = []

def load_data():
    # No need to load data, MongoDB is now handling this
    pass

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard-consultant", response_class=HTMLResponse)
async def consultant_dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard_consultant.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("user_dashboard.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/api/register")
async def register_user(user: User):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    users_collection.insert_one(user.dict())
    return {"message": "User registered successfully"}

@app.post("/api/login")
async def login_user(login_data: LoginData):
    user = users_collection.find_one({
        "email": login_data.email,
        "password": login_data.password
    })
    if user:
        return {"user": {"name": user["name"], "email": user["email"]}}
    raise HTTPException(status_code=401, detail="Invalid email or password")

@app.post("/book", response_model=BookingWithId)
async def book_slot(booking: Booking):
    booking_id = str(uuid4())
    booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_booking = BookingWithId(id=booking_id, booking_time=booking_time, **booking.dict())
    bookings_collection.insert_one(new_booking.dict())
    return new_booking

@app.get("/bookings", response_model=list[BookingWithId])
async def get_bookings():
    results = list(bookings_collection.find({}, {'_id': 0}))  # exclude _id
    return results

@app.delete("/bookings/{booking_id}", response_model=BookingWithId)
async def delete_booking(booking_id: str):
    booking = bookings_collection.find_one({"id": booking_id}, {'_id': 0})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    bookings_collection.delete_one({"id": booking_id})
    return booking

@app.post("/logout")
async def logout():
    return JSONResponse(content={"message": "Logged out successfully"})

# Load data at startup (removed as MongoDB is managing data)
load_data()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

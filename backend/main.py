from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from bcrypt import hashpw, gensalt, checkpw
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
import uvicorn
import os

# Initialize FastAPI app
app = FastAPI()

# Initialize the Jinja2Templates for rendering HTML
templates = Jinja2Templates(directory="templates")

# MongoDB Atlas connection
connection_string = "mongodb+srv://banking_user:Mpendulo00@bankingappdb.4zq89p5.mongodb.net/?retryWrites=true&w=majority&appName=BankingAppDB"
client = MongoClient(connection_string)
db = client["bankingappdb"]
users_collection = db["users"]
bookings_collection = db["bookings"]

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

# Route for the homepage (index)
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route for login page
@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Route for registration page
@app.get("/register", response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Route for user dashboard
@app.get("/user_dashboard", response_class=HTMLResponse)
async def get_user_dashboard(request: Request):
    return templates.TemplateResponse("user_dashboard.html", {"request": request})

# Route for consultant dashboard
@app.get("/consultant_dashboard", response_class=HTMLResponse)
async def get_consultant_dashboard(request: Request):
    return templates.TemplateResponse("dashboard_consultant.html", {"request": request})

# Registration endpoint
@app.post("/register")
async def register_user(user: User):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")
    
    hashed_password = hashpw(user.password.encode('utf-8'), gensalt())
    new_user = {"name": user.name, "email": user.email, "password": hashed_password}
    users_collection.insert_one(new_user)
    
    return JSONResponse(status_code=201, content={"message": "User registered successfully"})

# Login endpoint
@app.post("/api/login")
async def login_user(login_data: LoginData):
    # Check if email and password match the admin credentials
    if login_data.email == "admin@gmail.com" and login_data.password == "123":
        # Redirect to consultant dashboard if credentials match
        return RedirectResponse(url="/consultant_dashboard")
    
    # Otherwise, check if the user exists in the MongoDB database
    user = users_collection.find_one({"email": login_data.email})
    if user and checkpw(login_data.password.encode('utf-8'), user["password"]):
        return {"user": {"name": user["name"], "email": user["email"]}}
    
    # If email or password is invalid, raise an error
    raise HTTPException(status_code=401, detail="Invalid email or password")

# Booking endpoint
@app.post("/book", response_model=BookingWithId)
async def book_slot(booking: Booking):
    booking_id = str(uuid4())
    booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_booking = BookingWithId(id=booking_id, booking_time=booking_time, **booking.dict())
    bookings_collection.insert_one(new_booking.dict())
    return new_booking

# Retrieve bookings
@app.get("/bookings", response_model=list[BookingWithId])
async def get_bookings():
    results = list(bookings_collection.find({}, {'_id': 0}))
    return results

# Delete a booking
@app.delete("/bookings/{booking_id}", response_model=BookingWithId)
async def delete_booking(booking_id: str):
    booking = bookings_collection.find_one({"id": booking_id}, {'_id': 0})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    bookings_collection.delete_one({"id": booking_id})
    return booking

# Logout endpoint
@app.post("/logout")
async def logout():
    return JSONResponse(content={"message": "Logged out successfully"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

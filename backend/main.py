import os
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# ✅ Updated MongoDB URI with the new password
MONGODB_URI = "mongodb+srv://banking_user:Mpendulo123@bankingappdb.4zq89p5.mongodb.net/?retryWrites=true&w=majority&appName=BankingAppDB"
client = AsyncIOMotorClient(MONGODB_URI)
db = client["banking_app"]
users_collection = db["users"]
bookings_collection = db["bookings"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
async def register(user: User):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    await users_collection.insert_one(user.dict())
    return {"message": "User registered successfully"}

@app.post("/api/login")
async def login_user(login_data: LoginData):
    existing_user = await users_collection.find_one({"email": login_data.email})
    if not existing_user or existing_user["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"user": {"name": existing_user["name"], "email": existing_user["email"]}}

@app.post("/submit")
async def submit_booking(request: Request, name: str = Form(...), email: str = Form(...), service: str = Form(...)):
    booking = {
        "name": name,
        "email": email,
        "service": service
    }
    await bookings_collection.insert_one(booking)
    return templates.TemplateResponse("register.html", {"request": request, "success": True})

@app.post("/book", response_model=BookingWithId)
async def book_slot(booking: Booking):
    booking_id = str(uuid4())
    booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    booking_dict = {**booking.dict(), "id": booking_id, "booking_time": booking_time}
    await bookings_collection.insert_one(booking_dict)
    return booking_dict

@app.get("/bookings", response_model=list[BookingWithId])
async def get_bookings():
    results = []
    async for b in bookings_collection.find():
        results.append(BookingWithId(**b))
    return results

@app.delete("/bookings/{booking_id}", response_model=BookingWithId)
async def delete_booking(booking_id: str):
    deleted = await bookings_collection.find_one_and_delete({"id": booking_id})
    if not deleted:
        raise HTTPException(status_code=404, detail="Booking not found")
    return BookingWithId(**deleted)

@app.post("/logout")
async def logout():
    return JSONResponse(content={"message": "Logged out successfully"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

import os
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import uvicorn
from dotenv import load_dotenv

# Initialize FastAPI app
app = FastAPI()
load_dotenv()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",  # local frontend
        "http://localhost:8000",  # fallback
        "https://mybankingapp-ed37f0d6c39a.herokuapp.com/",  # add this if deploying frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable is not set.")
client = AsyncIOMotorClient(MONGO_URI)
db = client["banking_db"]
users_collection = db["users"]
bookings_collection = db["bookings"]

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

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

# Routes

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
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = hash_password(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_pwd
    
    await users_collection.insert_one(user_dict)
    return {"message": "User registered successfully"}

@app.post("/api/login")
async def login_user(login_data: LoginData):
    user = await users_collection.find_one({"email": login_data.email})
    if user and verify_password(login_data.password, user["password"]):
        return {"user": {"name": user["name"], "email": user["email"]}}
    raise HTTPException(status_code=401, detail="Invalid email or password")

@app.post("/book", response_model=BookingWithId)
async def book_slot(booking: Booking):
    booking_id = str(uuid4())
    booking_time = datetime.now(timezone.utc).isoformat()
    new_booking = BookingWithId(id=booking_id, booking_time=booking_time, **booking.dict())
    await bookings_collection.insert_one(new_booking.dict())
    return new_booking

@app.get("/bookings", response_model=list[BookingWithId])
async def get_bookings():
    bookings_cursor = bookings_collection.find()
    result = []
    async for booking in bookings_cursor:
        result.append(BookingWithId(**booking))
    return result

@app.delete("/bookings/{booking_id}", response_model=BookingWithId)
async def delete_booking(booking_id: str):
    result = await bookings_collection.find_one_and_delete({"id": booking_id})
    if not result:
        raise HTTPException(status_code=404, detail="Booking not found")
    return BookingWithId(**result)

@app.post("/logout")
async def logout():
    return JSONResponse(content={"message": "Logged out successfully"})

# Start server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

import os
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field, validator
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables early (locally)
load_dotenv()
logger.info("Loading environment variables...")

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    logger.error("MONGO_URI environment variable is not set!")
    raise RuntimeError("MONGO_URI environment variable is not set.")

# Initialize FastAPI app
app = FastAPI(title="Booking API", debug=True)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Setup templates directory
base_dir = os.getcwd()
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB async client & DB setup with connection verification
try:
    client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.get_default_database()
    logger.info(f"Connected to MongoDB database: {db.name}")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

users_collection = db["users"]
bookings_collection = db["bookings"]

# Middleware to log requests and responses
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            logger.debug(f"Request body: {body.decode()}")
    except Exception:
        pass
    
    response = await call_next(request)
    
    response.headers.update({
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
    })
    
    return response

# Enhanced exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    logger.error(f"Validation error: {errors}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": errors,
            "body": await request.body() if request.method in ["POST", "PUT"] else None
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Password validation function
def validate_password(password: str) -> str:
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long")
    return password

# Pydantic models with enhanced validation
class User(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="John Doe")
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., min_length=6, example="securepassword123")
    
    @validator('password')
    def password_complexity(cls, v):
        return validate_password(v)

class LoginData(BaseModel):
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., example="securepassword123")

class Booking(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="John Doe")
    id_number: str = Field(..., min_length=6, max_length=20, example="A123456")
    email: EmailStr = Field(..., example="john@example.com")
    selected_bank: str = Field(..., min_length=1, example="Bank of America")
    selected_service: str = Field(..., min_length=1, example="Loan Consultation")

class BookingWithId(Booking):
    id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    booking_time: str = Field(..., example="2023-01-01T12:00:00Z")

# Database health check endpoint
@app.get("/api/health")
async def health_check():
    try:
        # Test database connection
        await client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "error": str(e)}
        )

# Enhanced registration endpoint
@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: User):
    logger.info(f"Registration attempt for email: {user.email}")
    
    try:
        # Check for existing user
        existing = await users_collection.find_one({"email": user.email})
        if existing:
            logger.warning(f"Email already registered: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Email already registered",
                    "suggestion": "Try logging in or use a different email"
                }
            )

        # Hash password and prepare user document
        hashed_pwd = hash_password(user.password)
        user_dict = user.dict(exclude={"password"})
        user_dict.update({
            "password": hashed_pwd,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })

        # Insert new user
        result = await users_collection.insert_one(user_dict)
        logger.info(f"New user created with ID: {result.inserted_id}")
        
        return {
            "message": "User registered successfully",
            "user": {
                "name": user.name,
                "email": user.email
            }
        }
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error"
        )

# The rest of your endpoints (login, bookings, etc.) can follow the same enhanced pattern...

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_config=None,  # Use default logging
        reload=True
    )
from pydantic import BaseModel, EmailStr

class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str

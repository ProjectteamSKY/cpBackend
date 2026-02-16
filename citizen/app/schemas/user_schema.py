from pydantic import BaseModel, EmailStr


class RegisterSchema(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    contact: str | None = None


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str

    class Config:
        from_attributes = True

# auth.py
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Optional
from db import users_collection
# --- Load environment variables ---
load_dotenv()

# --- Initialize Router ---
router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- MongoDB Connection ---


# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- JWT Config ---
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


# --- Pydantic Models ---
class UserRegister(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    educationLevel: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: EmailStr
    educationLevel: str


# --- Helper Functions ---
def hash_password(password: str) -> str:
    """Hash plain password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against its hashed version."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generate a JWT token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# --- Routes ---

@router.post("/register", response_model=UserOut)
def register_user(user: UserRegister):
    """Register a new user."""
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)

    new_user = {
        "firstName": user.firstName,
        "lastName": user.lastName,
        "email": user.email,
        "password": hashed_password,
        "educationLevel": user.educationLevel,
        "createdAt": datetime.utcnow(),
    }

    result = users_collection.insert_one(new_user)

    return UserOut(
        id=str(result.inserted_id),
        firstName=user.firstName,
        lastName=user.lastName,
        email=user.email,
        educationLevel=user.educationLevel,
    )


@router.post("/login")
def login_user(user: UserLogin):
    """Authenticate a user and return a JWT token."""
    db_user = users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(db_user["_id"]), "email": db_user["email"]})
    return {"access_token": token, "token_type": "bearer"}


# --- Token Validation ---
def get_current_user(authorization: Optional[str] = Header(None)):
    """Decode the JWT token from 'Authorization: Bearer <token>' header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("email")
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# --- Profile Route ---
@router.get("/profile", response_model=UserOut)
def get_profile(current_user=Depends(get_current_user)):
    """Return the logged-in user's profile."""
    return UserOut(
        id=str(current_user["_id"]),
        firstName=current_user["firstName"],
        lastName=current_user["lastName"],
        email=current_user["email"],
        educationLevel=current_user["educationLevel"],
    )
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from . import models, database
from pydantic import BaseModel
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os

# JWT Configuration
SECRET_KEY = "PNYtraining" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiry time

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Pydantic models for token and user
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str

# Utility functions for authentication
def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        # we can log this error to investigate JWT-related issues in the future
        print(f"JWT decode error: {e}")
        raise credentials_exception

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Registration Endpoint
def register_user(user_create: UserCreate, db: Session):
    db_user = get_user(db, user_create.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash the user's password before saving it
    user = models.User(username=user_create.username, password=get_password_hash(user_create.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Login Endpoint
def login_user(form_data: OAuth2PasswordRequestForm, db: Session):
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

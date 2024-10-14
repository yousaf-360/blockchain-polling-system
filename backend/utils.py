from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from models import User
from database import db
import json
import os
import hashlib
from base64 import b64encode, b64decode

 
# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
 
# JWT settings
SECRET_KEY = "ABC!@#$*&^S&"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Web3 settings
# Password hashing functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
 
def get_password_hash(password):
    return pwd_context.hash(password)
 
# Encode private key function
def encode_private_key(private_key: str) -> str:
    return b64encode(private_key.encode()).decode('utf-8')
 
# Decode private key function
def decode_private_key(encoded_key: str) -> str:
    return b64decode(encoded_key).decode('utf-8')
 
# JWT token creation function
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
 
# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
 
# Get current user function
def get_current_user(token: str = Depends(oauth2_scheme)):
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
    except JWTError:
        raise credentials_exception
    user = db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    print(user)
    return User(**user)
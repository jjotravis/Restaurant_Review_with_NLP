from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from Controllers.AuthController import  Auth, get_auth_service #verify_password, verify_token
from Pydantic_Models.UserModel import UserBase
from Controllers.UserController import UserService, get_user_service
from Utilities.Db import SessionLocal
from sqlalchemy.orm import Session
from Utilities.Db import get_db
from jose import JWTError    

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_auth_service)):
    try:
        username = db.verify_token(token, db)  # Pass the session (db) to verify the token
        user = db.query(UserBase).filter(UserBase.username == username).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_current_active_user(current_user: UserBase = Depends(get_current_user)):
    if current_user.role not in ["USER", "ADMIN"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user

def get_current_admin_user(current_user: UserBase = Depends(get_current_user)):
    if current_user is None or current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user

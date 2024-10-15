from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from AuthController import  Auth #verify_password, verify_token
from Pydantic_Models.UserModel import UserBase
from Controllers.UserController import UserService
from Utilities.Db import SessionLocal
from sqlalchemy.orm import Session
from Utilities.Db import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = Auth.verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = UserService(db).get_user_by_username(payload.get("sub"))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def get_current_active_user(current_user: UserBase = Depends(get_current_user)):
    if current_user.role not in ["USER", "ADMIN"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user

def get_current_admin_user(current_user: UserBase = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user

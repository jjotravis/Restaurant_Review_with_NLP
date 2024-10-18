#!/usr/bin/env python3
from fastapi import Depends
from sqlalchemy.orm import Session
from Utilities.Db import get_db
from Models.User import User
from Pydantic_Models.UserModel import UserCreate, UserUpdate
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_users(self):
        return self.db.query(User).all()

    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.user_id == user_id).first()

    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, user: UserCreate):
        if not user.username or not user.password:
            raise ValueError("Username and password are required for user creation.")
        hashed_password = pwd_context.hash(user.password)
        user.password = hashed_password
        db_user = User(**user.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(self, user: UserUpdate):
        db_user = self.db.query(User).filter(User.user_id == user.user_id).first()
        if db_user:
            db_user.username = user.username
            db_user.password = pwd_context.hash(user.password)
            db_user.review_count = user.review_count
            db_user.role = user.role
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int):
        db_user = self.db.query(User).filter(User.user_id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)
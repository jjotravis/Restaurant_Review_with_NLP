# import os
# import logging
# from passlib.context import CryptContext
# from jose import JWTError, jwt
# from datetime import datetime, timedelta
# from typing import Optional
# from sqlalchemy.orm import Session
# from fastapi import Depends, HTTPException
# from Utilities.Db import get_db
# from Models.Token import Token
# import secrets


# SECRET_KEY = secrets.token_hex(32)
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# class Auth:
#     def __init__(self, db: Session):
#         self.db = db
        

#     def verify_password(self, plain_password, hashed_password):
#         return pwd_context.verify(plain_password, hashed_password)

#     def get_password_hash(self, password):
#         return pwd_context.hash(password)

#     def create_access_token(self, data: dict, expires_delta: timedelta = None, user_id: int = None):
#         to_encode = data.copy()
#         if expires_delta:
#             expire = datetime.utcnow() + expires_delta
#         else:
#             expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         to_encode.update({"exp": expire})
#         encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
#         # Store the token in the database
#         if self.db and user_id:
#             new_token = Token(token=encoded_jwt, user_id=user_id, expires_at=expire)
#             self.db.add(new_token)
#             self.db.commit()
#             self.db.refresh(new_token)
        
#         return encoded_jwt

#     @staticmethod
#     def verify_token(self, token: str, db: Session):
#         """Decode and verify the JWT token against the database."""
#         try:
#             payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#             username: str = payload.get("sub")  # Get the username from the token payload
#             if username is None:
#                 raise HTTPException(status_code=403, detail="Invalid token")
            
#             # Check if token exists in the database and is still valid
#             db_token = self.db.query(Token).filter(Token.token == token).first()
#             if not db_token or db_token.expires_at < datetime.utcnow():
#                 raise HTTPException(status_code=401, detail="Token expired or invalid")

#             return username
#         except JWTError:
#             raise HTTPException(status_code=403, detail="Invalid token")
#     # def verify_token(token: str, db: Session):
#     #     try:
#     #         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#     #         username: str = payload.get("sub")
#     #         if username is None:
#     #             raise HTTPException(status_code=403, detail="Invalid token")
            
#     #         # Check if token exists in the database and is still valid
#     #         db_token = db.query(Token).filter(Token.token == token).first()
#     #         if not db_token or db_token.expires_at < datetime.utcnow():
#     #             raise HTTPException(status_code=401, detail="Token expired or invalid")

#     #         return username
#     #     except JWTError:
#     #         raise HTTPException(status_code=403, detail="Invalid token")

# def get_auth_service(db: Session = Depends(get_db)) -> Auth:
#     return Auth(db)

import os
import logging
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from Utilities.Db import get_db
from Models.Token import Token
from Pydantic_Models.UserModel import UserBase
import secrets

# Secret key for JWT encoding/decoding
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Auth Class
class Auth:
    def __init__(self, db: Session):
        self.db = db

    def verify_password(self, plain_password, hashed_password):
        """Verify if the given plain password matches the hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        """Generate a password hash from a plain password."""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: timedelta = None, user_id: int = None):
        """Create a JWT token and store it in the database."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})  # Add expiration to token payload
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Encode the JWT
        
        # Store the token in the database
        if self.db and user_id:
            new_token = Token(token=encoded_jwt, user_id=user_id, expires_at=expire)
            self.db.add(new_token)
            self.db.commit()
            self.db.refresh(new_token)
        
        return encoded_jwt

    def verify_token(self, token: str):
        """Decode and verify the JWT token against the database."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")  # Get the username from the token payload
            if username is None:
                raise HTTPException(status_code=403, detail="Invalid token")
            
            # Check if token exists in the database and is still valid
            db_token = self.db.query(Token).filter(Token.token == token).first()
            if not db_token or db_token.expires_at < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Token expired or invalid")

            return username
        except JWTError:
            raise HTTPException(status_code=403, detail="Invalid token")

    def get_current_user(self, token: str):
        """Get the current user based on the token."""
        username = self.verify_token(token)  # Decode and verify the token
        user = self.db.query(UserBase).filter(UserBase.username == username).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user

    def get_current_active_user(self, current_user: UserBase):
        """Ensure the current user is active and has appropriate permissions."""
        if current_user.role not in ["USER", "ADMIN"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return current_user

    def get_current_admin_user(self, current_user: UserBase):
        """Ensure the current user has admin privileges."""
        if current_user is None or current_user.role != "ADMIN":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return current_user

# Dependency to get the auth service with a database session
def get_auth_service(db: Session = Depends(get_db)) -> Auth:
    return Auth(db)

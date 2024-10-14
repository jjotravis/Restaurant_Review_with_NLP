from sqlalchemy import Column, Integer, String
from Utilities.Db import Base


class User(Base):
    __tablename__ = 'Users'
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    review_count = Column(Integer, default=0)
    role = Column(String)
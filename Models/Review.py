from sqlalchemy import Column, Integer, String, Text
from Utilities.Db import Base

class Review(Base):
    __tablename__ = 'Reviews'
    
    review_id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    description = Column(String(300), default="You can eat here if you have no other way to go")
    user_id = Column(Integer, nullable=False)
    restaurant_id = Column(Integer, nullable=False)
    sentiment = Column(String(50), nullable=True)  # Add sentiment column

from sqlalchemy import  Column, String, Integer
from Utilities.Db import Base

# Define the Admin model
class Admin(Base):
    __tablename__ = "Admins"
    
    admin_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, default='Captain')
    role = Column(String, default='ADMIN')

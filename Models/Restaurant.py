from sqlalchemy import Column, Integer, String, Sequence
from Utilities.Db import Base

class Restaurant(Base):
    __tablename__ = 'Restaurants'

    restaurant_id = Column(Integer, Sequence('restaurant_id_seq'), primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    address = Column(String, unique=True, nullable=False)
    cuisine = Column(String, nullable=False)
    average_rating = Column(Integer, default=0)

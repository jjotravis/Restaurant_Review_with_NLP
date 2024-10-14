from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from Pydantic_Models.RestaurantModel import  RestaurantCreate,RestaurantUpdate
from Models.Restaurant import Restaurant
from Utilities.Db import get_db
from sqlalchemy.orm import Session

class RestaurantService:
    def __init__(self, db: Session):
        self.db = db

    def get_restaurants(self, skip: int = 0, limit: int = 10):
        return self.db.query(Restaurant).offset(skip).limit(limit).all()

    def get_restaurant(self, restaurant_id: int):
        return self.db.query(Restaurant).filter(Restaurant.restaurant_id == restaurant_id).first()

    def create_restaurant(self, restaurant: RestaurantCreate):
        db_restaurant = Restaurant(**restaurant.dict())
        self.db.add(db_restaurant)
        self.db.commit()
        self.db.refresh(db_restaurant)
        return db_restaurant

    def update_restaurant(self, restaurant_id: int, restaurant: RestaurantUpdate):
        db_restaurant = self.db.query(Restaurant).filter(Restaurant.restaurant_id == restaurant_id).first()
        if db_restaurant:
            for key, value in restaurant.dict().items():
                setattr(db_restaurant, key, value)
            self.db.commit()
            self.db.refresh(db_restaurant)
            return db_restaurant
        return None

    def delete_restaurant(self, restaurant_id: int):
        db_restaurant = self.db.query(Restaurant).filter(Restaurant.restaurant_id == restaurant_id).first()
        if db_restaurant:
            self.db.delete(db_restaurant)
            self.db.commit()
            return True
        return False
    
def get_restaurant_service(db: Session = Depends(get_db)) -> RestaurantService:
    return RestaurantService(db)
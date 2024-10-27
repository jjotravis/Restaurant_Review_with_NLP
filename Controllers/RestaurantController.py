from fastapi import Depends
from Pydantic_Models.RestaurantModel import RestaurantCreate, RestaurantUpdate
from sqlalchemy.orm import Session
from Models.Restaurant import Restaurant
from Utilities.Db import get_db
from Utilities.redis import RedisClient, get_redis

class RestaurantService:
    def __init__(self, db: Session = Depends(get_db), redis_client: RedisClient = Depends(get_redis)):
        self.db = db
        self.redis_client = redis_client

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
            self.redis_client.remove_restaurant(str(db_restaurant.restaurant_id))  # Remove from leaderboard
            return True
        return False

    def get_leaderboard(self, top_n: int = 10):
        leaderboard = self.redis_client.get_top_restaurants(top_n)
        return leaderboard

# Dependency for API
def get_restaurant_service(db: Session = Depends(get_db), redis_client: RedisClient = Depends(get_redis)) -> RestaurantService:
    return RestaurantService(db, redis_client)
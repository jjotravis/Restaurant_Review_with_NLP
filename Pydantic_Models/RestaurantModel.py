from pydantic import BaseModel

class RestaurantBase(BaseModel):
    name: str
    address: str
    cuisine: str
    average_rating: int = 0

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(RestaurantBase):
    pass

class RestaurantInDB(RestaurantBase):
    restaurant_id: int

    class Config:
        from_attributes = True

# main.py or your FastAPI app file

from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from Pydantic_Models.AdminModel import AdminCreate, AdminUpdate, AdminResponse
from Pydantic_Models.RestaurantModel import RestaurantCreate, RestaurantUpdate, RestaurantInDB
from Pydantic_Models.ReviewModel import ReviewCreate, ReviewResponse, ReviewUpdate
from Pydantic_Models.UserModel import UserCreate, UserResponse, UserUpdate, UserBase
from Controllers.AdminController import AdminService, get_admin_service
from Controllers.RestaurantController import RestaurantService, get_restaurant_service
from Controllers.ReviewController import ReviewService, get_review_service
from Controllers.UserController import UserService, get_user_service
from AuthController import Auth, get_auth_service
from Security import get_current_user, get_current_active_user, get_current_admin_user


app = FastAPI()

@app.get("/admin", response_model=List[AdminResponse], status_code=status.HTTP_200_OK)
def  get_all_admins(service: AdminService = Depends(get_admin_service)):
    try:
        return service.get_all_admins()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/admin/{admin_id}", response_model=AdminResponse)
async def get_admin_by_id(admin_id: int, service: AdminService = Depends(get_admin_service)):
    return service.get_admin_by_id(admin_id)

@app.get("/admin/username/{username}", response_model=AdminResponse)
async def get_admin_by_username(username: str, service: AdminService = Depends(get_admin_service)):
    return service.get_admin_by_username(username)

@app.post("/admin/add", response_model=AdminResponse)
def create_admin(admin: AdminCreate, service: AdminService = Depends(get_admin_service)):
    return service.create_admin(admin)

@app.put("/admin/update", response_model=AdminResponse)
async def update_admin(admin: AdminUpdate, service: AdminService = Depends(get_admin_service)):
    return service.update_admin(admin)

@app.delete("/admin/delete/{admin_id}")
async def delete_admin(admin_id: int, service: AdminService = Depends(get_admin_service)):
    return service.delete_admin(admin_id)

@app.get("/api/restaurant", response_model=list[RestaurantInDB])
def read_restaurants(skip: int = 0, limit: int = 10, service: RestaurantService = Depends(get_restaurant_service)):
    return  service.get_restaurants(skip, limit)

@app.get("/api/restaurant/{restaurant_id}", response_model=RestaurantInDB)
async def read_restaurant(restaurant_id: int, service: RestaurantService = Depends(get_restaurant_service)):
    restaurant = service.get_restaurant(restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@app.post("/api/restaurant", response_model=RestaurantInDB, status_code=status.HTTP_201_CREATED)
async def create_restaurant_endpoint(restaurant: RestaurantCreate, service: RestaurantService = Depends(get_restaurant_service)):
    return service.create_restaurant(restaurant)

@app.put("/api/restaurant/{restaurant_id}", response_model=RestaurantInDB)
async def update_restaurant_endpoint(restaurant_id: int, restaurant: RestaurantUpdate, service: RestaurantService = Depends(get_restaurant_service)):
    updated_restaurant = service.update_restaurant(restaurant_id, restaurant)
    if updated_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return updated_restaurant

@app.delete("/api/restaurant/{restaurant_id}", response_model=str)
async def delete_restaurant_endpoint(restaurant_id: int, service: RestaurantService = Depends(get_restaurant_service)):
    success = service.delete_restaurant(restaurant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return "Restaurant deleted successfully"

# async def get_review_service(db: Session = Depends(get_review_service)) -> ReviewService:
#     return ReviewService(db)

@app.get("/reviews/", response_model=List[ReviewResponse])
async def get_all_reviews(service: ReviewService = Depends(get_review_service)):
    return  service.get_all_reviews()

@app.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int, service: ReviewService = Depends(get_review_service)):
    review = service.get_review_by_id(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@app.get("/reviews/rating/{rating}", response_model=List[ReviewResponse])
async def get_reviews_by_rating(rating: int, service: ReviewService = Depends(get_review_service)):
    return service.get_reviews_by_rating(rating)

@app.get("/reviews/user/{user_id}", response_model=List[ReviewResponse])
async def get_reviews_by_user(user_id: int, service: ReviewService = Depends(get_review_service)):
    return service.get_reviews_by_user_id(user_id)

@app.get("/reviews/restaurant/{restaurant_id}", response_model=List[ReviewResponse])
async def get_reviews_by_restaurant(restaurant_id: int, service: ReviewService = Depends(get_review_service)):
    return service.get_reviews_by_restaurant_id(restaurant_id)

@app.post("/reviews/", response_model=ReviewResponse)
async def create_review(review: ReviewCreate, service: ReviewService = Depends(get_review_service)):
    return service.create_review(review)

@app.put("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: int, review: ReviewUpdate, service: ReviewService = Depends(get_review_service)):
    updated_review = await service.update_review(review_id, review)
    if updated_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return updated_review

@app.get("/api/user", response_model=list[UserResponse])
async def read_all_users(service: Session = Depends(get_user_service)):
    return service.get_all_users()

@app.get("/api/user/id/{user_id}", response_model=UserResponse)
async def read_user_by_id(user_id: int, service: Session = Depends(get_user_service)):
    user = service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/user/username/{username}", response_model=UserResponse)
async def read_user_by_username(username: str, service: Session = Depends(get_user_service)):
    user = service.get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/user/add", response_model=UserResponse)
async def create_new_user(user: UserCreate, service: Session = Depends(get_user_service)):
    db_user = service.create_user(user)
    return db_user

@app.put("/api/user/update", response_model=UserResponse)
async def update_existing_user(user: UserUpdate, service: Session = Depends(get_user_service)):
    db_user = service.update_user(user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/api/user/delete/{user_id}")
async def delete_existing_user(user_id: int, service: Session = Depends(get_user_service)):
    if not service.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}

@app.post("/token")
async def login(user: UserBase, service: Session = Depends(get_auth_service)):
    db_user = service.get_user_by_username(user.username)
    if db_user and Auth.verify_password(user.password, db_user.password):
        access_token = Auth.create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Protected routes
@app.get("/api/user", response_model=UserResponse)
async def read_all_users(current_user: UserBase = Depends(get_current_active_user), service: Session = Depends(get_auth_service)):
    return service.get_all_users()

@app.get("/api/user/id/{user_id}", response_model=UserResponse)
async def read_user_by_id(user_id: int, current_user: UserBase = Depends(get_current_active_user), service: Session = Depends(get_auth_service)):
    user = service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# @app.post("/api/user/add", response_model=UserResponse)
# async def create_new_user(user: UserCreate, db: Session = Depends(get_auth_service)):
#     service = UserService(db)
#     db_user = service.create_user(user)
#     return db_user

@app.put("/api/user/update", response_model=UserResponse)
async def update_existing_user(user: UserUpdate, current_user: UserBase = Depends(get_current_user), service: Session = Depends(get_auth_service)):
    db_user = service.update_user(user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/api/user/delete/{user_id}")
async def delete_existing_user(user_id: int, current_user: UserBase = Depends(get_current_admin_user), service: Session = Depends(get_auth_service)):
    if not service.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}
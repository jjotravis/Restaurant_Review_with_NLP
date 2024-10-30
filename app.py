from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta
from sqlalchemy.orm import Session
from typing import List, Tuple
from Pydantic_Models.AdminModel import AdminCreate, AdminUpdate, AdminResponse
from Pydantic_Models.RestaurantModel import RestaurantCreate, RestaurantUpdate, RestaurantInDB
from Pydantic_Models.ReviewModel import ReviewCreate, ReviewResponse, ReviewUpdate
from Pydantic_Models.UserModel import UserCreate, UserResponse, UserUpdate, UserBase, UserResponseLogin
from Pydantic_Models.TokenModel import TokenCreate
from Controllers.AdminController import AdminService, get_admin_service
from Controllers.RestaurantController import RestaurantService, get_restaurant_service
from Controllers.ReviewController import ReviewService, get_review_service
from Controllers.UserController import UserService, get_user_service
from Controllers.AuthController import Auth, get_auth_service
from Utilities.redis import RedisClient, get_redis


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Authentication dependencies
def get_current_user(token: str = Depends(oauth2_scheme), auth_service: Auth = Depends(get_auth_service)):
    return auth_service.get_current_user(token)

def get_current_active_user(current_user: UserBase = Depends(get_current_user), auth_service: Auth = Depends(get_auth_service)):
    return auth_service.get_current_active_user(current_user)

def get_current_admin_user(current_user: UserBase = Depends(get_current_user), auth_service: Auth = Depends(get_auth_service)):
    return auth_service.get_current_admin_user(current_user)

@app.post("/token", response_model=dict)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
    auth_service: Auth = Depends(get_auth_service)
):
    user = user_service.get_user_by_username(form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=20)
    
    access_token = auth_service.create_access_token(
        data={"sub": user.username, "user_id": user.user_id}, 
        expires_delta=access_token_expires,
        user_id=user.user_id
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/leaderboard", response_model=List[Tuple[str, float]])
def get_leaderboard(restaurant_service: RestaurantService = Depends(get_restaurant_service)):
    return restaurant_service.get_leaderboard()

@app.get("/restaurant_review/restaurant/ratings", response_model=List[Tuple[str, float]])
def get_all_restaurant_ratings(redis_client: RedisClient = Depends(get_redis)):
    return redis_client.get_all_restaurant_ratings()


@app.get("/restaurant_review/admin", response_model=List[AdminResponse], status_code=status.HTTP_200_OK)
def get_all_admins(
    current_user: UserBase = Depends(get_auth_service), 
    service: AdminService = Depends(get_admin_service)
):
    try:
        return service.get_all_admins()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


# @app.get("/restaurant_review/admin/{admin_id}", response_model=AdminResponse)
# async def get_admin_by_id(admin_id: int, service: AdminService = Depends(get_admin_service)):
#     return service.get_admin_by_id(admin_id)

# @app.get("/restaurant_review/admin/username/{username}", response_model=AdminResponse)
# async def get_admin_by_username(username: str, service: AdminService = Depends(get_admin_service)):
#     return service.get_admin_by_username(username)

# @app.post("/restaurant_review/admin/new", response_model=AdminResponse)
# def create_admin(admin: AdminCreate, service: AdminService = Depends(get_admin_service)):
#     return service.create_admin(admin)

# @app.put("/restaurant_review/admin/update", response_model=AdminResponse)
# async def update_admin(admin: AdminUpdate, service: AdminService = Depends(get_admin_service)):
#     return service.update_admin(admin)

# @app.delete("/restaurant_review/admin/delete/{admin_id}")
# async def delete_admin(admin_id: int, service: AdminService = Depends(get_admin_service)):
#     return service.delete_admin(admin_id)

@app.get("/restaurant_review/restaurant", response_model=list[RestaurantInDB])
def read_restaurants(skip: int = 0, limit: int = 10, service: RestaurantService = Depends(get_restaurant_service)):
    return  service.get_restaurants(skip, limit)

@app.get("/restaurant_review/restaurant/{restaurant_id}", response_model=RestaurantInDB)
async def read_restaurant(restaurant_id: int, service: RestaurantService = Depends(get_restaurant_service)):
    restaurant = service.get_restaurant(restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@app.post("/restaurant_review/restaurant", response_model=RestaurantInDB, status_code=status.HTTP_201_CREATED)
async def create_restaurant_endpoint(restaurant: RestaurantCreate, current_user: UserResponse = Depends(get_current_admin_user),service: RestaurantService = Depends(get_restaurant_service)):
    return service.create_restaurant(restaurant)

@app.put("/restaurant_review/restaurant/{restaurant_id}", response_model=RestaurantInDB)
async def update_restaurant_endpoint(restaurant_id: int, restaurant: RestaurantUpdate, current_user: UserResponse = Depends(get_current_admin_user),service: RestaurantService = Depends(get_restaurant_service)):
    updated_restaurant = service.update_restaurant(restaurant_id, restaurant)
    if updated_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return updated_restaurant

@app.delete("/restaurant_review/restaurant/{restaurant_id}", response_model=str)
async def delete_restaurant_endpoint(restaurant_id: int, current_user: UserResponse = Depends(get_current_admin_user),service: RestaurantService = Depends(get_restaurant_service)):
    success = service.delete_restaurant(restaurant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return "Restaurant deleted successfully"


@app.get("/restaurant_review/reviews/", response_model=List[ReviewResponse])
async def get_all_reviews(service: ReviewService = Depends(get_review_service)):
    return  service.get_all_reviews()

@app.get("/restaurant_review/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int, service: ReviewService = Depends(get_review_service)):
    review = service.get_review_by_id(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@app.get("/restaurant_review/reviews/rating/{rating}", response_model=List[ReviewResponse])
async def get_reviews_by_rating(rating: int, service: ReviewService = Depends(get_review_service)):
    return service.get_reviews_by_rating(rating)

@app.get("/restaurant_review/reviews/user", response_model=List[ReviewResponse])
async def get_reviews_by_user(
    service: ReviewService = Depends(get_review_service), 
    current_user: UserResponse = Depends(get_current_user)
):
    return service.get_reviews_by_user_id(current_user.user_id)

@app.get("/restaurant_review/reviews/restaurant/{restaurant_id}", response_model=List[ReviewResponse])
async def get_reviews_by_restaurant(restaurant_id: int, service: ReviewService = Depends(get_review_service)):
    return service.get_reviews_by_restaurant_id(restaurant_id)

@app.post("/restaurant_review/reviews/", response_model=ReviewResponse, )
async def create_review(review: ReviewCreate, current_user: UserResponse = Depends(get_current_user), service: ReviewService = Depends(get_review_service)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    return service.create_review(review, current_user.user_id)

@app.put("/restaurant_review/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: int, review: ReviewUpdate, current_user: UserResponse = Depends(get_current_user),service: ReviewService = Depends(get_review_service)):
    updated_review = await service.update_review(review_id, review)
    if updated_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return updated_review

@app.get("/restaurant_review/user", response_model=list[UserResponse])
async def read_all_users(service: Session = Depends(get_user_service)):
    return service.get_all_users()

@app.get("/restaurant_review/user/id/{user_id}", response_model=UserResponse)
async def read_user_by_id(user_id: int, service: Session = Depends(get_user_service)):
    user = service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/restaurant_review/user/username/{username}", response_model=UserResponseLogin)
async def read_user_by_username(username: str, service: Session = Depends(get_user_service)):
    user = service.get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@app.post("/restaurant_review/user/add", response_model=UserResponse)
async def create_new_user(user: UserCreate, current_user: UserResponse = Depends(get_current_admin_user),service: Session = Depends(get_user_service)):
    db_user = service.create_user(user)
    return db_user

@app.put("/restaurant_review/user/update", response_model=UserResponse)
async def update_existing_user(user: UserUpdate, current_user: UserResponse = Depends(get_current_admin_user),service: Session = Depends(get_user_service)):
    db_user = service.update_user(user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/restaurant_review/user/delete/{user_id}")
async def delete_existing_user(user_id: int, current_user: UserResponse = Depends(get_current_admin_user),service: Session = Depends(get_user_service)):
    if not service.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}

@app.get("/restaurant_review/user", response_model=UserResponse)
async def read_all_users(current_user: UserBase = Depends(get_current_active_user), service: Session = Depends(get_auth_service)):
    return service.get_all_users()

@app.get("/restaurant_review/user/id/{user_id}", response_model=UserResponse)
async def read_user_by_id(user_id: int, current_user: UserBase = Depends(get_current_active_user), service: Session = Depends(get_auth_service)):
    user = service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/restaurant_review/user/update", response_model=UserResponse)
async def update_existing_user(user: UserUpdate, current_user: UserBase = Depends(get_current_user), service: Session = Depends(get_auth_service)):
    db_user = service.update_user(user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/restaurant_review/user/delete/{user_id}")
async def delete_existing_user(user_id: int, current_user: UserBase = Depends(get_current_admin_user), service: Session = Depends(get_auth_service)):
    if not service.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}
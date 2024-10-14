# admin_service.py

from typing import List
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from Models.Admin import Admin as AdminModel  # Import the Admin model from the models file
from Utilities.Db import get_db  # Import the database session
from Pydantic_Models.AdminModel import AdminCreate, AdminUpdate, AdminResponse

class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_admins(self) -> List[AdminResponse]:
        admins = self.db.query(AdminModel).all()
        return [AdminResponse.model_validate(admin) for admin in admins]

    def get_admin_by_id(self, admin_id: int) -> AdminResponse:
        admin = self.db.query(AdminModel).filter(AdminModel.admin_id == admin_id).first()
        if admin is None:
            raise HTTPException(status_code=404, detail="Admin not found")
        return AdminResponse.model_validate(admin)

    def get_admin_by_username(self, username: str) -> AdminResponse:
        admin = self.db.query(AdminModel).filter(AdminModel.username == username).first()
        if admin is None:
            raise HTTPException(status_code=404, detail="Admin not found")
        return AdminResponse.model_validate(admin)

    def create_admin(self, admin_create: AdminCreate):#-> AdminResponse:
        if self.db.query(AdminModel).filter(AdminModel.username == admin_create.username).first():
            raise HTTPException(status_code=409, detail="Username already exists")
        
        admin = AdminModel(**admin_create.dict())
        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)
        # return AdminCreate.from_orm(admin)

    def update_admin(self, admin_update: AdminUpdate) -> AdminResponse:
        existing_admin = self.db.query(AdminModel).filter(AdminModel.admin_id == admin_update.admin_id).first()
        if existing_admin is None:
            raise HTTPException(status_code=404, detail="Admin not found")

        update_data = admin_update.model_dump(exclude_unset=True)
        for var, value in update_data.items():
            setattr(existing_admin, var, value)

        self.db.commit()
        self.db.refresh(existing_admin)
        return AdminResponse.model_validate(existing_admin)

    def delete_admin(self, admin_id: int) -> str:
        admin = self.db.query(AdminModel).filter(AdminModel.admin_id == admin_id).first()
        if admin is None:
            raise HTTPException(status_code=404, detail="Admin not found")

        self.db.delete(admin)
        self.db.commit()
        return "Admin deleted successfully"
# Dependency to provide an AdminService instance
def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(db)

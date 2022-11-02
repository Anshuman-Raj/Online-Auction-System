from fastapi import HTTPException
from db.models import Users
from sqlalchemy.orm import Session
import bcrypt
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    contact: str

def get_user(username: str, db: Session):
    user = db.query(Users).filter(Users.email == username).first()
    return user

def create_new_user(user: UserCreate, db: Session):
    is_present = get_user_by_email(user.email, db)
    if is_present is not None:
        raise HTTPException(status_code=409, detail='Email already registered')
    user = Users(
        username=user.username,
        email=user.email,
        password=bcrypt.hashpw(bytes(user.password, 'utf-8'), bcrypt.gensalt()).decode(),
        contact=user.contact
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(email: str, db: Session):
    user = db.query(Users).filter(Users.email == email).first()
    return user
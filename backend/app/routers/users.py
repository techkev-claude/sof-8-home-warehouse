from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.security import hash_password, require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserRead], dependencies=[Depends(require_admin)])
def list_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@router.post("/", response_model=UserRead, status_code=201, dependencies=[Depends(require_admin)])
def create_user(data: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == data.username)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(username=data.username, hashed_password=hash_password(data.password), role=data.role)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserRead, dependencies=[Depends(require_admin)])
def update_user(user_id: int, data: UserUpdate, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = data.dict(exclude_unset=True)
    if "password" in update_data:
        password = update_data.pop("password")
        if password:
            user.hashed_password = hash_password(password)
    for key, val in update_data.items():
        setattr(user, key, val)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()

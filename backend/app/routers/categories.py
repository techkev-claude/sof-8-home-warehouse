from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.models.category import Category
from app.models.item import Item
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from app.security import get_current_user, require_member

router = APIRouter(
    prefix="/categories", tags=["categories"], dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=List[CategoryRead])
def list_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()


@router.post("/", response_model=CategoryRead, status_code=201, dependencies=[Depends(require_member)])
def create_category(data: CategoryCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(Category).where(Category.name == data.name)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Category already exists")
    category = Category(**data.dict())
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryRead, dependencies=[Depends(require_member)])
def update_category(category_id: int, data: CategoryUpdate, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, val in data.dict(exclude_unset=True).items():
        setattr(category, key, val)
    session.commit()
    session.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204, dependencies=[Depends(require_member)])
def delete_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    in_use = session.exec(select(Item).where(Item.category_id == category_id)).first()
    if in_use:
        raise HTTPException(status_code=409, detail="Category is still in use by items")
    session.delete(category)
    session.commit()

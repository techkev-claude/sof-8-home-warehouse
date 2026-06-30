from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.models.usage_purpose import UsagePurpose
from app.models.item import Item
from app.schemas.usage_purpose import UsagePurposeCreate, UsagePurposeUpdate, UsagePurposeRead
from app.security import get_current_user, require_member

router = APIRouter(
    prefix="/usage-purposes", tags=["usage-purposes"], dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=List[UsagePurposeRead])
def list_purposes(session: Session = Depends(get_session)):
    return session.exec(select(UsagePurpose)).all()


@router.post("/", response_model=UsagePurposeRead, status_code=201, dependencies=[Depends(require_member)])
def create_purpose(data: UsagePurposeCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(UsagePurpose).where(UsagePurpose.name == data.name)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Usage purpose already exists")
    purpose = UsagePurpose(**data.dict())
    session.add(purpose)
    session.commit()
    session.refresh(purpose)
    return purpose


@router.patch("/{purpose_id}", response_model=UsagePurposeRead, dependencies=[Depends(require_member)])
def update_purpose(purpose_id: int, data: UsagePurposeUpdate, session: Session = Depends(get_session)):
    purpose = session.get(UsagePurpose, purpose_id)
    if not purpose:
        raise HTTPException(status_code=404, detail="Usage purpose not found")
    for key, val in data.dict(exclude_unset=True).items():
        setattr(purpose, key, val)
    session.commit()
    session.refresh(purpose)
    return purpose


@router.delete("/{purpose_id}", status_code=204, dependencies=[Depends(require_member)])
def delete_purpose(purpose_id: int, session: Session = Depends(get_session)):
    purpose = session.get(UsagePurpose, purpose_id)
    if not purpose:
        raise HTTPException(status_code=404, detail="Usage purpose not found")
    in_use = session.exec(select(Item).where(Item.usage_purpose_id == purpose_id)).first()
    if in_use:
        raise HTTPException(status_code=409, detail="Usage purpose is still in use by items")
    session.delete(purpose)
    session.commit()

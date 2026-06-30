import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional, List
from datetime import datetime

from app.config import settings
from app.database import get_session
from app.models.item import Item, ItemStatus
from app.models.item_image import ItemImage
from app.models.usage_purpose import UsagePurpose
from app.models.user import User
from app.schemas.item import ItemCreate, ItemUpdate, ItemRead, ItemCheckOut, ItemCheckIn
from app.security import get_current_user, require_member

router = APIRouter(prefix="/items", tags=["items"], dependencies=[Depends(get_current_user)])


def _to_read(session: Session, item: Item) -> ItemRead:
    images = session.exec(
        select(ItemImage).where(ItemImage.item_id == item.id).order_by(ItemImage.sort_order)
    ).all()
    return ItemRead.model_validate({**item.model_dump(), "images": images})


@router.get("/", response_model=List[ItemRead])
def list_items(
    status: Optional[ItemStatus] = None,
    category_id: Optional[int] = None,
    location_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    session: Session = Depends(get_session),
):
    query = select(Item)
    if status:
        query = query.where(Item.status == status)
    if category_id:
        query = query.where(Item.category_id == category_id)
    if location_id:
        query = query.where(Item.location_id == location_id)
    if search:
        query = query.where(Item.name.contains(search))
    items = session.exec(query.offset(skip).limit(limit)).all()
    return [_to_read(session, item) for item in items]


@router.post("/", response_model=ItemRead, status_code=201, dependencies=[Depends(require_member)])
def create_item(
    item: ItemCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_item = Item(
        **item.dict(),
        stored_at=datetime.utcnow(),
        created_by_id=current_user.id,
        updated_by_id=current_user.id,
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return _to_read(session, db_item)


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _to_read(session, item)


@router.patch("/{item_id}", response_model=ItemRead, dependencies=[Depends(require_member)])
def update_item(
    item_id: int,
    data: ItemUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, val in data.dict(exclude_unset=True).items():
        setattr(item, key, val)
    item.updated_by_id = current_user.id
    item.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(item)
    return _to_read(session, item)


@router.post("/{item_id}/checkout", response_model=ItemRead, dependencies=[Depends(require_member)])
def checkout_item(
    item_id: int,
    data: ItemCheckOut,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.status == ItemStatus.IN_USE:
        raise HTTPException(status_code=400, detail="Item already checked out")

    if data.usage_purpose_id is not None:
        purpose = session.get(UsagePurpose, data.usage_purpose_id)
        if not purpose:
            raise HTTPException(status_code=404, detail="Usage purpose not found")
        if purpose.requires_note and not data.usage_note:
            raise HTTPException(
                status_code=400,
                detail=f"Usage purpose '{purpose.name}' requires a usage_note",
            )

    item.status = ItemStatus.IN_USE
    item.usage_purpose_id = data.usage_purpose_id
    item.usage_note = data.usage_note
    item.checked_out_at = datetime.utcnow()
    item.location_id = None
    item.updated_by_id = current_user.id
    item.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(item)
    return _to_read(session, item)


@router.post("/{item_id}/checkin", response_model=ItemRead, dependencies=[Depends(require_member)])
def checkin_item(
    item_id: int,
    data: ItemCheckIn,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.status = ItemStatus.STORED
    item.location_id = data.location_id
    item.usage_purpose_id = None
    item.usage_note = None
    item.stored_at = datetime.utcnow()
    item.updated_by_id = current_user.id
    item.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(item)
    return _to_read(session, item)


@router.delete("/{item_id}", status_code=204, dependencies=[Depends(require_member)])
def delete_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    images = session.exec(select(ItemImage).where(ItemImage.item_id == item_id)).all()
    for image in images:
        for fname in (image.filename, image.thumbnail_filename):
            path = os.path.join(settings.images_path, fname)
            if os.path.exists(path):
                os.remove(path)
        session.delete(image)
    session.commit()
    session.delete(item)
    session.commit()

import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlmodel import Session, select
from typing import List

from app.config import settings
from app.database import get_session
from app.models.item import Item
from app.models.item_image import ItemImage
from app.schemas.item_image import ItemImageRead
from app.services.image_service import save_image
from app.security import get_current_user, require_member

router = APIRouter(prefix="/items", tags=["images"], dependencies=[Depends(get_current_user)])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.get("/{item_id}/images", response_model=List[ItemImageRead])
def list_images(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return session.exec(
        select(ItemImage).where(ItemImage.item_id == item_id).order_by(ItemImage.sort_order)
    ).all()


@router.post(
    "/{item_id}/images",
    response_model=List[ItemImageRead],
    status_code=201,
    dependencies=[Depends(require_member)],
)
async def upload_images(
    item_id: int,
    files: List[UploadFile] = File(...),
    session: Session = Depends(get_session),
):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    existing_count = len(
        session.exec(select(ItemImage).where(ItemImage.item_id == item_id)).all()
    )

    created: List[ItemImage] = []
    for index, file in enumerate(files):
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported image type: {file.content_type}")
        filename, thumb = await save_image(file, item_id)
        image = ItemImage(
            item_id=item_id,
            filename=filename,
            thumbnail_filename=thumb,
            is_primary=(existing_count == 0 and index == 0),
            sort_order=existing_count + index,
        )
        session.add(image)
        created.append(image)

    session.commit()
    for image in created:
        session.refresh(image)
    return created


@router.patch(
    "/{item_id}/images/{image_id}",
    response_model=ItemImageRead,
    dependencies=[Depends(require_member)],
)
def update_image(item_id: int, image_id: int, is_primary: bool, session: Session = Depends(get_session)):
    image = session.get(ItemImage, image_id)
    if not image or image.item_id != item_id:
        raise HTTPException(status_code=404, detail="Image not found")
    if is_primary:
        others = session.exec(
            select(ItemImage).where(ItemImage.item_id == item_id, ItemImage.id != image_id)
        ).all()
        for other in others:
            other.is_primary = False
            session.add(other)
    image.is_primary = is_primary
    session.commit()
    session.refresh(image)
    return image


@router.delete(
    "/{item_id}/images/{image_id}",
    status_code=204,
    dependencies=[Depends(require_member)],
)
def delete_image(item_id: int, image_id: int, session: Session = Depends(get_session)):
    image = session.get(ItemImage, image_id)
    if not image or image.item_id != item_id:
        raise HTTPException(status_code=404, detail="Image not found")
    for fname in (image.filename, image.thumbnail_filename):
        path = os.path.join(settings.images_path, fname)
        if os.path.exists(path):
            os.remove(path)
    was_primary = image.is_primary
    session.delete(image)
    session.commit()
    if was_primary:
        remaining = session.exec(
            select(ItemImage).where(ItemImage.item_id == item_id).order_by(ItemImage.sort_order)
        ).first()
        if remaining:
            remaining.is_primary = True
            session.commit()

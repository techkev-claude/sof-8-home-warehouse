import uuid
import os
from typing import Tuple
from PIL import Image
from app.config import settings

THUMB_SIZE = (300, 300)


async def save_image(file, item_id: int) -> Tuple[str, str]:
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"{item_id}_{uuid.uuid4().hex}.{ext}"
    thumb_name = f"thumb_{filename}"
    path = os.path.join(settings.images_path, filename)
    thumb_path = os.path.join(settings.images_path, thumb_name)

    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    with Image.open(path) as img:
        if ext in ("jpg", "jpeg") and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail(THUMB_SIZE)
        img.save(thumb_path)

    return filename, thumb_name

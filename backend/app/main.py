import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from app.config import settings
from app.database import create_db, engine
from app.models.user import User, UserRole
from app.security import hash_password
from app.routers import items, categories, locations, usage_purposes, images, auth, users

os.makedirs(settings.images_path, exist_ok=True)

app = FastAPI(title="Home Warehouse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_admin():
    with Session(engine) as session:
        has_user = session.exec(select(User)).first()
        if has_user:
            return
        admin = User(
            username=settings.admin_username,
            hashed_password=hash_password(settings.admin_password),
            role=UserRole.ADMIN,
        )
        session.add(admin)
        session.commit()


@app.on_event("startup")
def on_startup():
    create_db()
    seed_admin()


app.mount("/images", StaticFiles(directory=settings.images_path), name="images")

prefix = settings.api_prefix
app.include_router(auth.router, prefix=prefix)
app.include_router(users.router, prefix=prefix)
app.include_router(items.router, prefix=prefix)
app.include_router(categories.router, prefix=prefix)
app.include_router(locations.router, prefix=prefix)
app.include_router(usage_purposes.router, prefix=prefix)
app.include_router(images.router, prefix=prefix)


@app.get("/health")
def health():
    return {"status": "ok"}

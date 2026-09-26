from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.repositories import settings_repo

router = APIRouter()


class SettingsUpdate(BaseModel):
    default_extend_cm: float


@router.get("/settings")
def settings():
    return settings_repo.get_all()


@router.put("/settings")
def update_settings(body: SettingsUpdate):
    if body.default_extend_cm <= 0:
        raise HTTPException(422, "default_extend_cm must be positive")
    settings_repo.upsert("default_extend_cm", body.default_extend_cm)
    return settings_repo.get_all()

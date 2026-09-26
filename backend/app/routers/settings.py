from fastapi import APIRouter
from app.modules.uneven_ceiling import DEFAULT_EXTRA_CM, parse_extra_cm, validate_setting
from app.repositories import settings_repo
from app.schemas.settings import DefaultExtraCmRequest

router = APIRouter()


@router.get("/settings")
def settings():
    raw = settings_repo.get_all()
    # 同时给出解析后的数值，便于设置页直接回填
    raw["uneven_ceiling_extra_cm"] = str(
        parse_extra_cm(raw.get(settings_repo.UNEVEN_CEILING_EXTRA_CM_KEY), DEFAULT_EXTRA_CM)
    )
    return raw


@router.put("/settings/uneven-ceiling-extra-cm")
def update_default_extra_cm(body: DefaultExtraCmRequest):
    """设置页维护不齐顶默认加长厘米；只影响后续测算，不改写旧 run。"""
    validate_setting(body.extra_cm)
    value = float(body.extra_cm)
    settings_repo.upsert_setting(settings_repo.UNEVEN_CEILING_EXTRA_CM_KEY, str(value))
    return {"uneven_ceiling_extra_cm": value}

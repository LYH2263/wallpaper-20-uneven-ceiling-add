from fastapi import APIRouter, Query
from app.schemas.estimate import EstimateRequest
from app.services import estimate_service

router = APIRouter()


@router.get("/estimate")
def estimate_get(
    wall_id: int = Query(...),
    roll_id: int = Query(...),
    save: bool = False,
    uneven_ceiling: bool = False,
    extra_cm: float | None = Query(None),
):
    return estimate_service.run_estimate(
        wall_id, roll_id, save, "", uneven_ceiling, extra_cm
    )


@router.post("/estimate")
def estimate_post(body: EstimateRequest):
    return estimate_service.run_estimate(
        body.wall_id,
        body.roll_id,
        body.save,
        body.note,
        body.uneven_ceiling,
        body.extra_cm,
    )


@router.get("/estimate/uneven-ceiling-recommendation")
def uneven_ceiling_recommendation(wall_id: int = Query(...)):
    """墙面详情用：按设置页默认加长判断是否建议启用不齐顶加长。"""
    return estimate_service.recommend_for_wall(wall_id)

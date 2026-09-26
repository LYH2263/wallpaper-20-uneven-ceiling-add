from fastapi import HTTPException

from app.engines.wallpaper_math import roll_count
from app.modules.uneven_ceiling import (
    DEFAULT_EXTRA_CM,
    parse_extra_cm,
    validate_request,
)
from app.repositories import history, rolls, walls
from app.repositories.settings_repo import UNEVEN_CEILING_EXTRA_CM_KEY, get_setting


def _resolve_extra_cm(uneven_ceiling: bool, extra_cm: float | None) -> float:
    """启用但未显式给加长厘米时，取设置页维护的默认加长；关闭时归零。"""
    if not uneven_ceiling:
        return 0.0
    if extra_cm is None:
        return parse_extra_cm(get_setting(UNEVEN_CEILING_EXTRA_CM_KEY), DEFAULT_EXTRA_CM)
    return float(extra_cm)


def run_estimate(
    wall_id: int,
    roll_id: int,
    save: bool,
    note: str,
    uneven_ceiling: bool = False,
    extra_cm: float | None = None,
):
    wall = walls.get_wall(wall_id)
    if not wall:
        raise HTTPException(404, "wall not found")
    roll = rolls.get_roll(roll_id)
    if not roll:
        raise HTTPException(404, "roll not found")
    if wall.get("data_quality") == "dirty" or roll.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty seed entity")

    uneven_ceiling = bool(uneven_ceiling)
    extra_cm = _resolve_extra_cm(uneven_ceiling, extra_cm)
    # 启用但加长为负或为 0：拒绝
    validate_request(uneven_ceiling, extra_cm)

    calc = roll_count(
        wall["perimeter"],
        wall["height"],
        roll["width"],
        roll["length"],
        roll["pattern_cm"],
        uneven_ceiling,
        extra_cm,
    )

    run_id = None
    if save:
        # 落库钉住：写入时的加长厘米、开关与卷数（连同 drop_len 一起冻结进快照）
        snapshot = {
            **calc,
            "wall_id": wall_id,
            "roll_id": roll_id,
            "uneven_ceiling": calc["uneven_ceiling"],
            "extra_cm": calc["extra_cm"],
            "rolls": calc["rolls"],
        }
        run_id = history.insert_run(wall_id, roll_id, snapshot, note)
    return {"wall": wall, "roll": roll, "run_id": run_id, **calc}


def recommend_for_wall(wall_id: int) -> dict:
    """墙面详情用：以设置页默认加长试算各款 clean 卷，
    若对所有款卷数都不增加，则建议启用不齐顶加长。"""
    wall = walls.get_wall(wall_id)
    if not wall:
        raise HTTPException(404, "wall not found")
    extra_cm = parse_extra_cm(get_setting(UNEVEN_CEILING_EXTRA_CM_KEY), DEFAULT_EXTRA_CM)
    checked = []
    if wall.get("data_quality") != "dirty":
        for roll in rolls.list_rolls():
            if roll.get("data_quality") == "dirty":
                continue
            plain = roll_count(
                wall["perimeter"], wall["height"], roll["width"], roll["length"], roll["pattern_cm"]
            )
            longer = roll_count(
                wall["perimeter"], wall["height"], roll["width"], roll["length"], roll["pattern_cm"],
                True, extra_cm,
            )
            checked.append({
                "roll_id": roll["id"],
                "roll_name": roll["name"],
                "rolls_without": plain["rolls"],
                "rolls_with": longer["rolls"],
                "adds_roll": longer["rolls"] > plain["rolls"],
            })
    recommended = bool(checked) and all(not c["adds_roll"] for c in checked)
    return {
        "wall_id": wall_id,
        "recommended": recommended,
        "extra_cm": extra_cm,
        "checked": checked,
    }

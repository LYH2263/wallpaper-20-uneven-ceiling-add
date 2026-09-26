from fastapi import HTTPException

from app.engines.wallpaper_math import roll_count
from app.repositories import history, rolls, settings_repo, walls

DEFAULT_EXTEND_SETTING = "default_extend_cm"
DEFAULT_EXTEND_CM = 10.0


def run_estimate(
    wall_id: int,
    roll_id: int,
    save: bool,
    note: str,
    extend_enabled: bool = False,
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

    resolved_cm = 0.0
    if extend_enabled:
        if extra_cm is None:
            try:
                resolved_cm = float(
                    settings_repo.get_all().get(DEFAULT_EXTEND_SETTING, DEFAULT_EXTEND_CM)
                )
            except (TypeError, ValueError):
                resolved_cm = DEFAULT_EXTEND_CM
        else:
            resolved_cm = float(extra_cm)

    try:
        calc = roll_count(
            wall["perimeter"],
            wall["height"],
            roll["width"],
            roll["length"],
            roll["pattern_cm"],
            extend_enabled,
            resolved_cm,
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc))

    snapshot = {
        **calc,
        "extend_enabled": bool(extend_enabled),
        "extra_cm": resolved_cm if extend_enabled else 0.0,
        "wall_id": wall_id,
        "roll_id": roll_id,
    }
    run_id = None
    if save:
        run_id = history.insert_run(wall_id, roll_id, snapshot, note)
    return {"wall": wall, "roll": roll, "run_id": run_id, **snapshot}

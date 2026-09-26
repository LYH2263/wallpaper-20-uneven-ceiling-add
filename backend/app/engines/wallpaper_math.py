"""Wallpaper rolls: perimeter strips, pattern repeat on drop length, strips per roll."""

from app.engines.helpers import ceil_units, floor_units
from app.modules.uneven_ceiling import apply_extra, cm_to_m


def roll_count(
    perimeter: float,
    height: float,
    roll_width: float,
    roll_length: float,
    pattern_cm: float,
    uneven_ceiling: bool = False,
    extra_cm: float = 0.0,
) -> dict:
    if roll_width <= 0 or roll_length <= 0:
        raise ValueError("invalid roll size")
    drops = ceil_units(float(perimeter) / float(roll_width))
    pattern_m = max(0.0, float(pattern_cm) / 100.0)
    drop_len = float(height) + pattern_m
    if drop_len <= 0:
        raise ValueError("invalid drop length")

    # 分幅链路独立步骤：不齐顶加长（关闭时 drop_len 不变，结果与改造前一致）
    base_drop_len = drop_len
    drop_len = apply_extra(drop_len, uneven_ceiling, extra_cm)
    extra_m = round(drop_len - base_drop_len, 3)

    strips_per_roll = max(1, floor_units(float(roll_length) / drop_len))
    rolls = ceil_units(drops / strips_per_roll)
    return {
        "drops": drops,
        "drop_len_m": round(drop_len, 3),
        "pattern_m": round(pattern_m, 3),
        "strips_per_roll": strips_per_roll,
        "rolls": rolls,
        "uneven_ceiling": bool(uneven_ceiling) and cm_to_m(extra_cm) > 0,
        "extra_cm": float(extra_cm) if uneven_ceiling else 0.0,
        "extra_m": extra_m,
    }

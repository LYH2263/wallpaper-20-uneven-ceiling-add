"""Wallpaper rolls: perimeter strips, pattern repeat, uneven-ceiling extension, strips per roll.

分幅链路（有序独立步骤）：
1. compute_drops       周长 ÷ 纸宽 → 幅数
2. base_drop_len       墙高 + 对花余量 → 基础每条长度
3. apply_extension     不齐顶加长（独立步骤，仅启用时生效）
4. strips_per_roll     每卷可裁条数
5. total_rolls         总卷数
"""

from app.engines.helpers import ceil_units, floor_units


def compute_drops(perimeter: float, roll_width: float) -> int:
    if roll_width <= 0:
        raise ValueError("invalid roll size")
    return ceil_units(float(perimeter) / float(roll_width))


def base_drop_len(height: float, pattern_cm: float) -> tuple[float, float]:
    """返回 (基础每条长度 m, 对花余量 m)。"""
    pattern_m = max(0.0, float(pattern_cm) / 100.0)
    drop_len = float(height) + pattern_m
    if drop_len <= 0:
        raise ValueError("invalid drop length")
    return drop_len, pattern_m


def apply_extension(drop_len: float, extend_enabled: bool, extra_cm: float) -> tuple[float, float]:
    """不齐顶加长独立步骤：在既有每条长度上再增加固定厘米数（换算米）。

    关闭时原样返回（厘米被忽略，不报错）；启用且厘米 <= 0 时拒绝。
    返回 (最终每条长度 m, 加长量 m)。
    """
    if not extend_enabled:
        return drop_len, 0.0
    extra_m = float(extra_cm) / 100.0
    if extra_m <= 0:
        raise ValueError("extra_cm must be positive when uneven-ceiling extension is enabled")
    return drop_len + extra_m, extra_m


def strips_per_roll(roll_length: float, drop_len: float) -> int:
    if roll_length <= 0:
        raise ValueError("invalid roll size")
    return max(1, floor_units(float(roll_length) / drop_len))


def total_rolls(drops: int, strips_per_roll_count: int) -> int:
    return ceil_units(drops / strips_per_roll_count)


def roll_count(
    perimeter: float,
    height: float,
    roll_width: float,
    roll_length: float,
    pattern_cm: float,
    extend_enabled: bool = False,
    extra_cm: float = 0.0,
) -> dict:
    drops = compute_drops(perimeter, roll_width)
    base_len, pattern_m = base_drop_len(height, pattern_cm)
    final_len, _extra_m = apply_extension(base_len, extend_enabled, extra_cm)
    spr = strips_per_roll(roll_length, final_len)
    rolls = total_rolls(drops, spr)
    result = {
        "drops": drops,
        "drop_len_m": round(final_len, 3),
        "pattern_m": round(pattern_m, 3),
        "strips_per_roll": spr,
        "rolls": rolls,
    }
    if extend_enabled:
        result["extend_enabled"] = True
        result["extra_cm"] = extra_cm
        result["base_drop_len_m"] = round(base_len, 3)
    return result

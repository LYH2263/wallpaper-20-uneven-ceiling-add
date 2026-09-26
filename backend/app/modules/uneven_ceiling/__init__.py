"""不齐顶加长：分幅链路的独立步骤。

启用时在既有 drop_len（层高 + 花高匹配）之上再加固定厘米数，
换算为米后再进入每卷条数 / 卷数计算；关闭时链路与改造前一致。
加长厘米为负或为 0 且仍启用时拒绝。
"""

from fastapi import HTTPException

#: 设置页维护的默认加长厘米（settings 表缺省/脏值时回落到此值）
DEFAULT_EXTRA_CM = 10.0


def cm_to_m(extra_cm: float) -> float:
    return max(0.0, float(extra_cm)) / 100.0


def is_enabled(uneven_ceiling: bool, extra_cm: float) -> bool:
    """仅当开关打开且加长厘米严格为正时启用。"""
    return bool(uneven_ceiling) and float(extra_cm) > 0


def apply_extra(drop_len_m: float, uneven_ceiling: bool, extra_cm: float) -> float:
    """分幅链路中“不齐顶加长”这一步：在既有 drop_len 上追加固定厘米。

    关闭（或厘米非正）时原样返回；启用且厘米 <= 0 由调用方在入链前拒绝。
    """
    if not is_enabled(uneven_ceiling, extra_cm):
        return float(drop_len_m)
    return float(drop_len_m) + cm_to_m(extra_cm)


def validate_request(uneven_ceiling: bool, extra_cm: float) -> None:
    """测算入参校验：启用但加长厘米为负或为 0 时拒绝（422）。"""
    if bool(uneven_ceiling) and float(extra_cm) <= 0:
        raise HTTPException(422, "不齐顶加长启用时，加长厘米必须大于 0")


def parse_extra_cm(raw, fallback: float = DEFAULT_EXTRA_CM) -> float:
    """解析 settings 中存放的默认加长厘米，脏值回落到 fallback。"""
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return float(fallback)
    return value if value > 0 else float(fallback)


def validate_setting(extra_cm: float) -> None:
    """设置页保存默认加长：必须为正数，否则拒绝（422）。"""
    try:
        value = float(extra_cm)
    except (TypeError, ValueError):
        raise HTTPException(422, "默认加长厘米必须是数字")
    if value <= 0:
        raise HTTPException(422, "默认加长厘米必须大于 0")

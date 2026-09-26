import pytest

from app.engines.wallpaper_math import roll_count
from app.modules.uneven_ceiling import apply_extra, cm_to_m, is_enabled, validate_request
from fastapi import HTTPException


# --- 关闭时与改造前同参一致（等价性） ---

def test_disabled_matches_legacy_master_bed():
    r = roll_count(16.0, 2.7, 0.53, 10.0, 0)
    assert r["drops"] == 31
    assert r["drop_len_m"] == 2.7
    assert r["strips_per_roll"] == 3
    assert r["rolls"] == 11
    assert r["uneven_ceiling"] is False
    assert r["extra_m"] == 0.0

    # 即使传了 extra_cm，只要开关关闭也必须与改造前一致
    r2 = roll_count(16.0, 2.7, 0.53, 10.0, 0, uneven_ceiling=False, extra_cm=10)
    assert r2["drop_len_m"] == 2.7
    assert r2["strips_per_roll"] == 3
    assert r2["rolls"] == 11
    assert r2["extra_m"] == 0.0


def test_disabled_matches_legacy_pattern_wall():
    r = roll_count(20.0, 2.8, 0.53, 10.0, 64, uneven_ceiling=False, extra_cm=10)
    assert r["drop_len_m"] == 3.44
    assert r["strips_per_roll"] == 2
    assert r["rolls"] == 19


# --- 启用：在既有 drop_len 上追加固定厘米后再算条数/卷数 ---

def test_enabled_adds_ten_cm_without_extra_roll():
    # 2.7 + 0.10 = 2.80m；10m 卷仍可出 3 条 → 卷数不变
    r = roll_count(16.0, 2.7, 0.53, 10.0, 0, uneven_ceiling=True, extra_cm=10)
    assert r["drop_len_m"] == 2.8
    assert r["extra_m"] == 0.1
    assert r["uneven_ceiling"] is True
    assert r["extra_cm"] == 10.0
    assert r["strips_per_roll"] == 3
    assert r["rolls"] == 11


def test_enabled_can_add_a_roll():
    # 2.7 + 0.70 = 3.40m；每卷只出 2 条 → 卷数 11 → 16
    r = roll_count(16.0, 2.7, 0.53, 10.0, 0, uneven_ceiling=True, extra_cm=70)
    assert r["drop_len_m"] == 3.4
    assert r["strips_per_roll"] == 2
    assert r["rolls"] == 16


def test_enabled_on_pattern_wall():
    # 花高匹配后的 3.44m 再加 10cm
    r = roll_count(20.0, 2.8, 0.53, 10.0, 64, uneven_ceiling=True, extra_cm=10)
    assert r["drop_len_m"] == 3.54
    assert r["strips_per_roll"] == 2
    assert r["rolls"] == 19


def test_module_steps():
    assert cm_to_m(10) == 0.1
    assert apply_extra(2.7, True, 10) == pytest.approx(2.8)
    assert apply_extra(2.7, False, 10) == 2.7
    assert is_enabled(True, 10) is True
    assert is_enabled(True, 0) is False
    assert is_enabled(False, 10) is False


# --- 加长厘米为负或为 0 且仍启用时拒绝 ---

@pytest.mark.parametrize("bad", [0, -1, -15])
def test_reject_non_positive_when_enabled(bad):
    with pytest.raises(HTTPException) as ei:
        validate_request(True, bad)
    assert ei.value.status_code == 422


def test_non_positive_ok_when_disabled():
    validate_request(False, 0)  # 不抛

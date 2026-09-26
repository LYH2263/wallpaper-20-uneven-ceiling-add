import pytest

from app.engines.wallpaper_math import roll_count


def test_plain_master_bed():
    r = roll_count(16.0, 2.7, 0.53, 10.0, 0)
    assert r["drops"] == 31
    assert r["drop_len_m"] == 2.7
    assert r["strips_per_roll"] == 3
    assert r["rolls"] == 11


def test_pattern_wall():
    r = roll_count(20.0, 2.8, 0.53, 10.0, 64)
    assert r["drops"] == 38
    assert r["drop_len_m"] == 3.44
    assert r["strips_per_roll"] == 2
    assert r["rolls"] == 19


def test_disabled_dict_equals_baseline():
    base = roll_count(16.0, 2.7, 0.53, 10.0, 0)
    off = roll_count(16.0, 2.7, 0.53, 10.0, 0, extend_enabled=False, extra_cm=10)
    assert off == base
    assert set(off.keys()) == {"drops", "drop_len_m", "pattern_m", "strips_per_roll", "rolls"}


def test_enabled_extends_len_not_drops():
    r = roll_count(16.0, 2.7, 0.53, 10.0, 0, True, 10)
    assert r["drops"] == 31
    assert r["base_drop_len_m"] == 2.7
    assert r["drop_len_m"] == 2.8
    assert r["extend_enabled"] is True
    assert r["extra_cm"] == 10
    assert r["strips_per_roll"] == 3
    assert r["rolls"] == 11


def test_enabled_can_change_roll_count():
    off = roll_count(16.0, 3.3, 0.53, 10.0, 0)
    on = roll_count(16.0, 3.3, 0.53, 10.0, 0, True, 10)
    assert (off["strips_per_roll"], off["rolls"]) == (3, 11)
    assert (on["strips_per_roll"], on["rolls"]) == (2, 16)


def test_enabled_pattern_wall_delta():
    r = roll_count(20.0, 2.8, 0.53, 10.0, 64, True, 10)
    assert r["base_drop_len_m"] == 3.44
    assert r["drop_len_m"] == 3.54


@pytest.mark.parametrize("cm", [0, -5])
def test_enabled_nonpositive_cm_raises(cm):
    with pytest.raises(ValueError):
        roll_count(16.0, 2.7, 0.53, 10.0, 0, True, cm)

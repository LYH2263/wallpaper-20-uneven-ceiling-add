import pytest
from fastapi import HTTPException

from app.repositories import history, settings_repo
from app.services import estimate_service


def test_disabled_matches_baseline():
    out = estimate_service.run_estimate(1, 1, False, "")
    assert out["extend_enabled"] is False
    assert out["extra_cm"] == 0.0
    assert out["drops"] == 31
    assert out["drop_len_m"] == 2.7
    assert out["strips_per_roll"] == 3
    assert out["rolls"] == 11
    assert "base_drop_len_m" not in out


def test_enabled_explicit_cm():
    out = estimate_service.run_estimate(1, 1, False, "", True, 10)
    assert out["drop_len_m"] == 2.8
    assert out["base_drop_len_m"] == 2.7
    assert out["extra_cm"] == 10.0
    assert out["extend_enabled"] is True


def test_enabled_uses_settings_default():
    settings_repo.upsert("default_extend_cm", "12")
    out = estimate_service.run_estimate(1, 1, False, "", True, None)
    assert out["extra_cm"] == 12.0
    assert out["drop_len_m"] == 2.82


@pytest.mark.parametrize("cm", [0, -5])
def test_enabled_nonpositive_cm_rejected(cm):
    with pytest.raises(HTTPException) as exc:
        estimate_service.run_estimate(1, 1, False, "", True, cm)
    assert exc.value.status_code == 422


def test_saved_run_pins_switch_cm_and_ignores_later_setting_change():
    settings_repo.upsert("default_extend_cm", "15")
    saved = estimate_service.run_estimate(1, 1, True, "", True, None)
    run_id = saved["run_id"]
    assert run_id is not None

    run = history.get_run(run_id)
    assert run["result"]["extend_enabled"] is True
    assert run["result"]["extra_cm"] == 15.0
    assert run["result"]["drop_len_m"] == 2.85
    assert run["result"]["rolls"] == 11

    settings_repo.upsert("default_extend_cm", "25")
    run_again = history.get_run(run_id)
    assert run_again["result"]["extra_cm"] == 15.0
    assert run_again["result"]["drop_len_m"] == 2.85


def test_disabled_saved_run_pins_off_switch():
    saved = estimate_service.run_estimate(1, 1, True, "", False, None)
    run = history.get_run(saved["run_id"])
    assert run["result"]["extend_enabled"] is False
    assert run["result"]["extra_cm"] == 0.0
    assert run["result"]["drop_len_m"] == 2.7


def test_missing_and_dirty_entities():
    with pytest.raises(HTTPException) as exc:
        estimate_service.run_estimate(999, 1, False, "")
    assert exc.value.status_code == 404
    with pytest.raises(HTTPException) as exc:
        estimate_service.run_estimate(3, 1, False, "")
    assert exc.value.status_code == 422

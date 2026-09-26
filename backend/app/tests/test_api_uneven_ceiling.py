import os
import tempfile

# 必须在导入 app 之前钉住独立数据目录
_tmp = tempfile.mkdtemp(prefix="wp-test-")
os.environ["DATA_DIR"] = _tmp

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def test_estimate_disabled_is_legacy(client):
    r = client.get("/api/estimate", params={"wall_id": 1, "roll_id": 1})
    assert r.status_code == 200
    body = r.json()
    assert body["rolls"] == 11
    assert body["drop_len_m"] == 2.7
    assert body["uneven_ceiling"] is False
    assert body["extra_cm"] == 0.0


def test_enabled_uses_and_pins_snapshot(client):
    r = client.post(
        "/api/estimate",
        json={"wall_id": 1, "roll_id": 1, "save": True,
              "uneven_ceiling": True, "extra_cm": 70},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["drop_len_m"] == 3.4
    assert body["strips_per_roll"] == 2
    assert body["rolls"] == 16
    assert body["uneven_ceiling"] is True
    run_id = body["run_id"]
    assert run_id

    # 落库钉住加长厘米、开关与卷数
    saved = client.get("/api/runs").json()["items"]
    run = next(x for x in saved if x["id"] == run_id)
    assert run["result"]["rolls"] == 16
    assert run["result"]["uneven_ceiling"] is True
    assert run["result"]["extra_cm"] == 70.0
    assert run["result"]["drop_len_m"] == 3.4


def test_changing_default_does_not_rewrite_old_runs(client):
    # 先存一条默认加长下的 run
    created = client.post(
        "/api/estimate",
        json={"wall_id": 1, "roll_id": 1, "save": True, "uneven_ceiling": True},
    ).json()
    run_id = created["run_id"]
    old_drop = created["drop_len_m"]
    old_extra = created["extra_cm"]

    # 设置页改默认加长
    assert client.put("/api/settings/uneven-ceiling-extra-cm", json={"extra_cm": 5}).status_code == 200
    assert client.get("/api/settings").json()["uneven_ceiling_extra_cm"] == "5.0"

    # 新测算用新默认；旧 run 打开仍是写入时的值
    fresh = client.post(
        "/api/estimate",
        json={"wall_id": 1, "roll_id": 1, "uneven_ceiling": True},
    ).json()
    assert fresh["extra_cm"] == 5.0
    assert fresh["drop_len_m"] == 2.75

    run = next(x for x in client.get("/api/runs").json()["items"] if x["id"] == run_id)
    assert run["result"]["extra_cm"] == old_extra
    assert run["result"]["drop_len_m"] == old_drop


def test_reject_non_positive_extra(client):
    for bad in (0, -10):
        r = client.post(
            "/api/estimate",
            json={"wall_id": 1, "roll_id": 1, "uneven_ceiling": True, "extra_cm": bad},
        )
        assert r.status_code == 422


def test_reject_bad_default_setting(client):
    assert client.put("/api/settings/uneven-ceiling-extra-cm", json={"extra_cm": 0}).status_code == 422


def test_wall_recommendation(client):
    # 默认 5cm 对素色53不增卷（2.75m 仍出 3 条）→ 建议启用
    r = client.get("/api/estimate/uneven-ceiling-recommendation", params={"wall_id": 1})
    assert r.status_code == 200
    body = r.json()
    assert body["recommended"] is True
    assert body["extra_cm"] == 5.0
    assert any(c["roll_name"] == "素色53" and c["adds_roll"] is False for c in body["checked"])

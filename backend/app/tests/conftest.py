import os
import tempfile

import pytest
# 必须在导入 app 之前钉住独立数据目录
_tmp = tempfile.mkdtemp(prefix="wp-test-")
os.environ["DATA_DIR"] = _tmp

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    # 进入 with 才会触发 startup（建表 + seed）
    with TestClient(app) as c:
        yield c

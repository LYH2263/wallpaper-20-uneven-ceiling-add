import os
import tempfile

# 必须在导入 app.* 之前设置：app.config 在 import 时读取 DATA_DIR 并建目录
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="wp_tests_"))

from app import seed  # noqa: E402

seed.init_db()

from app.db import connect


def init_db():
    conn = connect()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS walls(
            id INTEGER PRIMARY KEY, name TEXT, perimeter REAL, height REAL,
            data_quality TEXT DEFAULT 'clean', note TEXT DEFAULT '',
            uneven_ceiling INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS rolls(
            id INTEGER PRIMARY KEY, name TEXT, width REAL, length REAL, pattern_cm REAL,
            data_quality TEXT DEFAULT 'clean', note TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS calc_runs(
            id INTEGER PRIMARY KEY AUTOINCREMENT, wall_id INTEGER, roll_id INTEGER,
            result_json TEXT, note TEXT, created_at TEXT
        );
        """
    )
    # 幂等迁移：旧库补 uneven_ceiling 列，并回填一面建议启用不齐顶加长的墙
    wall_cols = {r["name"] for r in conn.execute("PRAGMA table_info(walls)").fetchall()}
    if "uneven_ceiling" not in wall_cols:
        conn.execute(
            "ALTER TABLE walls ADD COLUMN uneven_ceiling INTEGER NOT NULL DEFAULT 0"
        )
        conn.execute("UPDATE walls SET uneven_ceiling=1 WHERE name='主卧一圈'")
    # 默认加长厘米（新库与旧库均保证存在，不覆盖已修改值）
    conn.execute("INSERT OR IGNORE INTO settings(key,value) VALUES ('default_extend_cm','10')")
    if conn.execute("SELECT COUNT(*) c FROM walls").fetchone()["c"] == 0:
        conn.executemany(
            "INSERT INTO walls(name,perimeter,height,data_quality,note,uneven_ceiling)"
            " VALUES (?,?,?,?,?,?)",
            [
                ("主卧一圈", 16.0, 2.7, "clean", "", 1),
                ("大花匹配", 20.0, 2.8, "clean", "需对花", 0),
                ("脏数据-零周长", 0.0, 2.7, "dirty", "周长为0", 0),
            ],
        )
        conn.executemany(
            "INSERT INTO rolls(name,width,length,pattern_cm,data_quality,note) VALUES (?,?,?,?,?,?)",
            [
                ("素色53", 0.53, 10.0, 0, "clean", ""),
                ("大花64", 0.53, 10.0, 64, "clean", ""),
                ("脏数据-零宽", 0.0, 10.0, 0, "dirty", ""),
            ],
        )
        conn.execute("INSERT INTO settings(key,value) VALUES ('unit','roll')")
    conn.commit()
    conn.close()

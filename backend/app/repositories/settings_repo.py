from app.db import connect


def get_all() -> dict:
    conn = connect()
    try:
        return {r["key"]: r["value"] for r in
                conn.execute("SELECT key,value FROM settings").fetchall()}
    finally:
        conn.close()


def upsert(key: str, value: str) -> None:
    conn = connect()
    try:
        conn.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)),
        )
        conn.commit()
    finally:
        conn.close()

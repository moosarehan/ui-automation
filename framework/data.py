import json
import os
import sqlite3
from pathlib import Path

from openpyxl import load_workbook
from redis import Redis

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def excel(key):
    book = load_workbook(FIXTURES / "accounts.xlsx", read_only=True)
    try:
        headers, *rows = book.active.values
        for row in rows:
            record = dict(zip(headers, row))
            if record["id"] == key:
                return record
    finally:
        book.close()
    raise KeyError(key)


def database(key):
    connection = sqlite3.connect((FIXTURES / "catalog.sqlite").as_uri() + "?mode=ro", uri=True)
    try:
        connection.row_factory = sqlite3.Row
        row = connection.execute("SELECT * FROM searches WHERE id = ?", (key,)).fetchone()
        if row is None:
            raise KeyError(key)
        return dict(row)
    finally:
        connection.close()


def redis_client():
    return Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True,
                          socket_connect_timeout=5, socket_timeout=5)


def reservation(key):
    with redis_client() as client:
        value = client.get("campus-supply:fixture:" + key)
    if value is None:
        raise KeyError(f"Missing Redis fixture {key}. Run python -m framework.seed_redis")
    return json.loads(value)


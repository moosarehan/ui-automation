import json
from .data import FIXTURES, redis_client

if __name__ == "__main__":
    records = json.loads((FIXTURES / "reservations.json").read_text(encoding="utf-8"))
    with redis_client() as client:
        client.mset({"campus-supply:fixture:" + key: json.dumps(value) for key, value in records.items()})


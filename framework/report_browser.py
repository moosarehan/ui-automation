"""Distinguish browser executions when combining Allure results from CI."""
import hashlib
import json
import sys
from pathlib import Path


def label_results(directory, browser):
    for path in Path(directory).glob("*-result.json"):
        result = json.loads(path.read_text(encoding="utf-8"))
        result.setdefault("parameters", []).append({"name": "browser", "value": browser})
        result["labels"] = [label for label in result.get("labels", []) if label["name"] != "parentSuite"]
        result["labels"].append({"name": "parentSuite", "value": browser})
        identity = result.get("historyId") or result["name"]
        result["historyId"] = hashlib.sha256(f"{identity}:{browser}".encode()).hexdigest()
        path.write_text(json.dumps(result), encoding="utf-8")


if __name__ == "__main__":
    label_results(*sys.argv[1:])


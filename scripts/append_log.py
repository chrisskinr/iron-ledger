#!/usr/bin/env python3
"""Append a log entry from the Log Reps shortcut (repository_dispatch payload via env vars)."""
import json, os, datetime
from zoneinfo import ZoneInfo

lift = os.environ.get("LIFT", "").strip().lower()
weight = os.environ.get("WEIGHT", "")
reps = os.environ.get("REPS", "")

ALIASES = {"bench": "c1", "incline": "c2", "ohp": "s1", "row": "b1", "squat": "l1"}
lift_id = ALIASES.get(lift, lift)  # accept either alias or raw id

entry = {
    "date": datetime.datetime.now(ZoneInfo("America/Chicago")).date().isoformat(),
    "lift": lift_id,
    "weight": float(weight) if weight else None,
    "worstSetReps": int(float(reps)) if reps else None,
    "processed": False,
}

path = "data/log.json"
log = []
if os.path.exists(path):
    with open(path) as f:
        log = json.load(f)
log.append(entry)
with open(path, "w") as f:
    json.dump(log, f, indent=2)

print(f"Logged: {entry}")

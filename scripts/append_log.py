#!/usr/bin/env python3
"""Append log entries from the dashboard (batch) or Log Reps shortcut (single)."""
import json, os, datetime
from zoneinfo import ZoneInfo

ALIASES = {"bench": "c1", "incline": "c2", "ohp": "s1", "row": "b1", "squat": "l1"}

def today():
    return os.environ.get("DATE_OVERRIDE") or datetime.datetime.now(ZoneInfo("America/Chicago")).date().isoformat()

def to_entry(lift, weight, reps):
    lift = str(lift or "").strip().lower()
    return {
        "date": today(),
        "lift": ALIASES.get(lift, lift),
        "weight": float(weight) if weight not in (None, "") else None,
        "worstSetReps": int(float(reps)) if reps not in (None, "") else None,
        "processed": False,
    }

new = []
raw = os.environ.get("ENTRIES", "")
if raw and raw not in ("null", "[]"):
    for e in json.loads(raw):
        new.append(to_entry(e.get("lift"), e.get("weight"), e.get("reps")))
else:
    lift = os.environ.get("LIFT", "")
    if lift:
        new.append(to_entry(lift, os.environ.get("WEIGHT", ""), os.environ.get("REPS", "")))

path = "data/log.json"
log = []
if os.path.exists(path):
    with open(path) as f:
        log = json.load(f)
log.extend(new)
with open(path, "w") as f:
    json.dump(log, f, indent=2)

print(f"Logged {len(new)} entr{'y' if len(new)==1 else 'ies'}: {new}")

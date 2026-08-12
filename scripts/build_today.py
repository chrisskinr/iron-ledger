#!/usr/bin/env python3
"""Applies unprocessed rep logs to progression, then builds today.txt (the morning SMS body)."""
import json, os, datetime
from zoneinfo import ZoneInfo

def fmt(x):
    return int(x) if float(x).is_integer() else x

with open("plan.json") as f:
    plan = json.load(f)
with open("data/progression.json") as f:
    prog = json.load(f)

log_path = "data/log.json"
log = []
if os.path.exists(log_path):
    with open(log_path) as f:
        log = json.load(f)

# ---- apply progression: latest unprocessed entry per lift wins ----
changes = []
latest = {}
for e in log:
    if not e.get("processed") and e.get("lift") in prog["lifts"]:
        latest[e["lift"]] = e  # log is chronological; last one sticks

for lift_id, e in latest.items():
    rules = prog["lifts"][lift_id]
    logged_w = e.get("weight")
    reps = e.get("worstSetReps")
    if logged_w is not None:
        prog["weights"][lift_id] = logged_w  # trust the logged weight as current
    cur = prog["weights"][lift_id]
    if reps is not None and cur is not None:
        if reps >= rules["repTop"]:
            new = cur + rules["increment"]
            prog["weights"][lift_id] = new
            changes.append(f"{rules['name']}: {fmt(cur)} → {fmt(new)} {rules['unit']} (owned the top of the range)")
        elif reps < rules["repBottom"]:
            changes.append(f"{rules['name']}: hold {fmt(cur)} {rules['unit']} (build back to {rules['repBottom']}+)")
        else:
            changes.append(f"{rules['name']}: hold {fmt(cur)} {rules['unit']} (get every set to {rules['repTop']})")

for e in log:
    e["processed"] = True

with open("data/progression.json", "w") as f:
    json.dump(prog, f, indent=2)
with open(log_path, "w") as f:
    json.dump(log, f, indent=2)

# ---- build today.txt ----
tz = ZoneInfo(plan.get("timezone", "America/Chicago"))
today = datetime.date.fromisoformat(os.environ["DATE_OVERRIDE"]) if os.environ.get("DATE_OVERRIDE") else datetime.datetime.now(tz).date()

# ---- log-driven rotation: the day advances only after a logged session ----
if "currentDayIndex" not in prog:
    prog["currentDayIndex"] = 0
latest_log_date = max((e["date"] for e in log), default=None)
if latest_log_date and latest_log_date != prog.get("lastAdvanceLogDate"):
    prog["currentDayIndex"] = (prog["currentDayIndex"] + 1) % len(plan["rotation"])
    prog["lastAdvanceLogDate"] = latest_log_date
travel = plan.get("travel")
in_travel = bool(travel) and today <= datetime.date.fromisoformat(travel["until"])
rotation = travel["rotation"] if in_travel else plan["rotation"]
idx = prog["currentDayIndex"] % len(rotation)
day = rotation[idx]

with open("data/progression.json", "w") as f:
    json.dump(prog, f, indent=2)

def w_of(ex_id):
    w = prog["weights"].get(ex_id)
    if w is None:
        return ""
    unit = prog["lifts"][ex_id]["unit"]
    wtxt = int(w) if float(w).is_integer() else w
    return f"{wtxt} {unit} · "

tier_labels = {1: "IF YOU ONLY HAVE 10 MIN", 2: "GOT 25 MIN — ADD", 3: "FULL SESSION — ADD"}
if in_travel:
    tier_labels = {int(k): v for k, v in travel.get("tierLabels", {}).items()} or tier_labels

emoji = "🏨" if in_travel else "🏋️"
mode = " · HOTEL MODE" if in_travel else ""
lines = [f"{emoji} {day['day'].upper()} DAY{mode} — {today.strftime('%a %b %-d')}"]
if day.get("rehab"):
    lines.append("⚠️ Knee: pain-free reps only. Sharp pain = rack it.")
lines.append("")
for tier in (1, 2, 3):
    items = [e for e in day["exercises"] if e["tier"] == tier]
    if not items:
        continue
    lines.append(tier_labels[tier] + ":")
    for e in items:
        lines.append(f"• {e['name']} — {w_of(e['id'])}{e['detail']}")
    lines.append("")
if changes:
    lines.append("📈 SINCE LAST TIME:")
    for c in changes:
        lines.append(f"• {c}")
    lines.append("")
lines.append("DAILY (always):")
for b in plan["baseline"]:
    lines.append(f"• {b['name']}")
lines.append("")
lines.append("Log it: https://chrisskinr.github.io/iron-ledger/")
lines.append("Log reps: shortcuts://run-shortcut?name=Log%20Reps")

with open("today.txt", "w") as f:
    f.write("\n".join(lines))
print("\n".join(lines))

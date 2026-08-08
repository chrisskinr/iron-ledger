# The Iron Ledger

Priority-ordered daily lifting plan on a 2-day cycle (Chest+Back / Legs+Shoulders, antagonist supersets) + streak dashboard + morning SMS. Basement edition: everything under 7 ft, no pull-up bar required, knee-rehab-aware.

## What's in here

| File | Purpose |
|---|---|
| `index.html` | The dashboard (GitHub Pages). Check off work, track streaks, log squat rehab load. Data lives in your phone's localStorage. |
| `plan.json` | Source of truth for the rotation. Edit this to change exercises. |
| `scripts/build_today.py` | Builds `today.txt` — the SMS body — from `plan.json`. |
| `.github/workflows/daily-brief.yml` | Runs the script every morning at 5:15 AM Central and commits `today.txt`. |

## Deploy (5 minutes from the Mac Mini)

1. Create a repo (e.g. `iron-ledger`), push these files to `main`.
2. Repo → Settings → Pages → Deploy from branch → `main` / root.
3. Dashboard is live at `https://chrisskinr.github.io/iron-ledger/`. Add it to your phone's home screen.
4. In `scripts/build_today.py`, replace the `Log it:` URL with your real Pages URL. Run the workflow once manually (Actions tab → Build daily workout brief → Run workflow) to generate the first `today.txt`.

## iOS Shortcut (the morning text)

Two-action Shortcut, then an Automation to fire it:

1. **Shortcuts app → + → New Shortcut**
   - Action 1: **Get Contents of URL** → `https://raw.githubusercontent.com/chrisskinr/iron-ledger/main/today.txt`
   - Action 2: **Send Message** → message = the URL contents → recipient = yourself. (Or use **Show Notification** if you'd rather not have it in Messages.)
2. **Automation tab → + → Time of Day** → 6:30 AM daily → Run Immediately (no confirmation) → pick your Shortcut.

The GitHub Action rebuilds `today.txt` at 5:15 AM Central, so by 6:30 the text always reflects the correct rotation day.

## iOS Shortcut #2 — "Log Reps" (the feedback loop)

Replying to the SMS does nothing (nothing is listening to your Messages) — instead the morning text ends with a `shortcuts://` link that opens this. Three taps and tomorrow's text carries the new weight.

**One-time: create a GitHub token.** GitHub → Settings → Developer settings → Fine-grained personal access token → scope it to just this repo → Repository permissions → Contents: Read and write. Copy it.

**Build the Shortcut (name it exactly `Log Reps`):**
1. **Choose from Menu** — options: `bench`, `incline`, `ohp`, `row`, `squat`
2. **Ask for Input** (Number) — "Weight?"
3. **Ask for Input** (Number) — "Worst-set reps?"
4. **Get Contents of URL** → `https://api.github.com/repos/chrisskinr/iron-ledger/dispatches`
   - Method: POST
   - Headers: `Authorization` = `Bearer YOUR-TOKEN` · `Accept` = `application/vnd.github+json`
   - Request Body (JSON): `event_type` = `log`; `client_payload` = dictionary with `lift` (menu result), `weight` (first input), `reps` (second input)

The `log-reps` workflow appends your entry, reruns the progression engine, and commits. Log as many lifts per session as you want — run the Shortcut once per lift.

## How progression works (double progression)

Each tracked lift has a rep range. **Own the top of the range on your worst set → weight goes up next cycle.** Miss the bottom → hold and rebuild. In between → hold until you own it.

| Lift | Range | Start | Increment |
|---|---|---|---|
| Barbell bench | 4×6–8 | 175 lb (from your 210×2) | +5 |
| DB incline | 3×8–10 | 50/hand | +5/hand |
| Seated DB OHP | 3×8–10 | 50/hand | +5/hand |
| One-arm DB row | 4×8–10/side | log first session to set it | +5/hand |
| Box squat | 4×8 | 50 lb (bar + 2.5s) | +2.5, pain-free only |

Weights live in `data/progression.json` — edit it directly anytime to override the engine.

## How the goal/streak works

A day counts as **hit** when every Tier-1 item (the 10-minute essentials) **plus** the daily baseline (lymph circuit + 100 V-sits) is checked. Tier 2 and 3 make the day better; they don't gate the streak. Ten rushed minutes before a shower keeps the chain alive — that's by design.

## Editing the plan

Change `plan.json` (exercise names, sets, tiers) and mirror the change in the `PLAN` object at the top of `index.html`'s script block. Two spots for now — a build step can unify them later.

## Knee rehab note

Leg day Tier 1 is the box squat at rehab load with a hard rule: add 2.5–5 lb only when every rep is pain-free. The dashboard logs load over time so you can see the climb back. If you're working with a PT, their protocol wins over anything in this plan.

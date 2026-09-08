# tools/

## brief.py — the session briefing

Run this at the start of every session, before answering anything:

```
python3 tools/brief.py            # today
python3 tools/brief.py 2026-09-13 # any date
```

It prints, from the live data:

- bodyweight: last reading, rolling average, week-over-week rate against the 0.2–0.4 %/week target
- this week: sessions done, hard sets per muscle against the weekly target, daily macro averages
- the last 10 days of food
- the exercise board: every exercise's last performance and the load to prescribe next
  (double progression, straight from `dashboard/index.html`, which is the single source of truth
  for the program)
- patterns the numbers reveal by themselves: first set too light, every set on the same round
  number, share of sets with no RIR, days with fat over and carbs under target, sleep
- which session is next in the rolling order

## Keeping the data fresh

The athlete's phone writes into the dashboard artifact database. Pull it into `data/db/` at the
start of a session with the Artifact tool (three calls, one per collection):

```
Artifact action=read_db db_op=list collection=sessions   out_dir=data/db
Artifact action=read_db db_op=list collection=nutrition  out_dir=data/db
Artifact action=read_db db_op=list collection=bodyweight out_dir=data/db
```

url = https://claude.ai/code/artifact/b7cdec67-42a2-4075-bd10-a4e797e91546

`data/db/` is the machine-readable mirror. The markdown in `logs/` stays the human-readable record
and the reasoning; `profile/patterns.md` holds the behaviour rules that the numbers cannot express.

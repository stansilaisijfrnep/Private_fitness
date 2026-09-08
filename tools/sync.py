#!/usr/bin/env python3
"""Flatten the dashboard database into queryable tables.

data/db/**            the raw documents pulled out of the artifact database
      ↓ sync.py
data/sets.csv         one row per logged set, ever
data/meals.csv        one row per logged meal item, ever
data/bodyweight.csv   one row per morning reading, ever

Everything downstream (tools/brief.py, any analysis) reads these three files, so a number is
computed once and never re-derived by hand. Run it after pulling the database.
"""
import csv, json, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB, OUT = ROOT / "data" / "db", ROOT / "data"


def docs(coll):
    d = DB / coll
    return [json.loads(p.read_text()) for p in sorted(d.glob("*.json"))] if d.is_dir() else []


def write(name, header, rows):
    with (OUT / name).open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return len(rows)


def main():
    sets = []
    for s in sorted(docs("sessions"), key=lambda x: x.get("date", "")):
        if s.get("type") == "sport":
            continue
        for ex in s.get("exercises", []):
            for i, t in enumerate(ex.get("sets", []), 1):
                if not t.get("reps"):
                    continue
                load, reps = t.get("load"), t["reps"]
                e1rm = round(load * (1 + reps / 30), 1) if load else None
                sets.append([s["date"], s.get("dayKey", ""), s.get("week", ""), ex["k"], ex.get("n", ""),
                             i, "" if load is None else load, reps, "" if t.get("rir") is None else t["rir"],
                             "" if e1rm is None else e1rm, (ex.get("note") or "").replace("\n", " ")])
    n_sets = write("sets.csv", ["date", "day", "week", "exercise_key", "exercise", "set_no",
                                "load_kg", "reps", "rir", "e1rm_kg", "exercise_note"], sets)

    meals = []
    for n in sorted(docs("nutrition"), key=lambda x: x.get("date", "")):
        for m in n.get("meals", []):
            meals.append([n["date"], m.get("slot", "snack"), m.get("time", ""), m.get("name", ""),
                          m.get("kcal", 0), m.get("protein", 0), m.get("carbs", 0), m.get("fat", 0)])
    n_meals = write("meals.csv", ["date", "slot", "time", "meal", "kcal", "protein_g", "carbs_g", "fat_g"], meals)

    bw = []
    for b in sorted(docs("bodyweight"), key=lambda x: x.get("date", "")):
        if b.get("weight"):
            bw.append([b["date"], b["weight"], b.get("waist", ""), (b.get("note") or "").replace("\n", " ")])
    # rolling 7-day average, computed here so nobody recomputes it by hand
    rows = []
    for i, (d, w, waist, note) in enumerate(bw):
        day = dt.date.fromisoformat(d)
        win = [x[1] for x in bw if 0 <= (day - dt.date.fromisoformat(x[0])).days <= 6]
        rows.append([d, w, round(sum(win) / len(win), 2), waist, note])
    n_bw = write("bodyweight.csv", ["date", "weight_kg", "avg7_kg", "waist_cm", "note"], rows)

    print(f"sets.csv {n_sets} rows · meals.csv {n_meals} rows · bodyweight.csv {n_bw} rows")


if __name__ == "__main__":
    main()

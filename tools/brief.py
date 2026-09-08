#!/usr/bin/env python3
"""Session briefing: everything the coach needs to know, from the live data.

Reads the JSON dumped out of the dashboard database into data/db/ (sessions,
nutrition, bodyweight) plus the program in dashboard/index.html, and prints one
compact briefing: the week so far, volume per muscle, every exercise's last
performance and next target, the bodyweight trend, and the behaviour patterns
the numbers themselves reveal.

Usage:  python3 tools/brief.py [YYYY-MM-DD]
"""
import json, re, sys, datetime as dt
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "db"

# Which muscles each exercise pays into. Used for weekly hard-set counting.
MUSCLES = {
    "bench": ["chest", "triceps"], "incdb": ["chest", "triceps"], "dips": ["chest", "triceps"],
    "pecdeck": ["chest"], "cablefly": ["chest"],
    "csrow": ["back"], "dbrow": ["back"], "tbarrow": ["back"], "cablerow": ["back"], "pullup": ["back", "biceps"],
    "sapd": ["back"], "revpec": ["rear delts"],
    "ohp": ["shoulders", "triceps"], "dbohp": ["shoulders", "triceps"], "dblat": ["side delts"],
    "ezcurl": ["biceps"], "inccurl": ["biceps"], "hammer": ["biceps"],
    "pushdown": ["triceps"], "ohtri": ["triceps"],
    "squat": ["quads", "glutes"], "legpress": ["quads", "glutes"], "lunge": ["quads", "glutes"],
    "bss": ["quads", "glutes"], "legext": ["quads"],
    "rdl": ["hamstrings", "glutes"], "trapbar": ["hamstrings", "glutes", "back"],
    "legcurl": ["hamstrings"], "nordic": ["hamstrings"],
    "hanglr": ["abs"], "abwheel": ["abs"], "copenhagen": ["abs"], "landing": [],
}
TARGET_SETS = {"chest": (10, 20), "back": (10, 20), "shoulders": (6, 12), "side delts": (8, 16),
               "biceps": (8, 16), "triceps": (8, 16), "quads": (10, 20), "hamstrings": (8, 16),
               "glutes": (8, 16), "abs": (6, 12), "rear delts": (6, 12)}


def load(coll):
    d = DB / coll
    return [json.loads(p.read_text()) for p in sorted(d.glob("*.json"))] if d.is_dir() else []


def program():
    """Single source of truth: the PROGRAM object inside the dashboard."""
    src = (ROOT / "dashboard" / "index.html").read_text()
    body = src.split("const PROGRAM = ", 1)[1].split("\n};", 1)[0] + "}"
    # Quote the unquoted JS keys, but never touch anything inside a string literal.
    parts = re.split(r'("(?:[^"\\]|\\.)*")', body)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r'([{,\s])([A-Za-z_][A-Za-z0-9_]*)\s*:', r'\1"\2":', parts[i])
    return json.loads("".join(parts))


def monday(d):
    return d - dt.timedelta(days=d.weekday())


def fmt_sets(sets, added=False):
    out = []
    for s in sets:
        if not s.get("reps"):
            continue
        load_ = s.get("load")
        if load_ is None or (added and not load_):
            tag = "bw"
        elif added:
            tag = f"+{load_:g}"
        else:
            tag = f"{load_:g}"
        out.append(f"{tag}×{s['reps']:g}")
    return " ".join(out)


def e1rm(load_, reps):
    return load_ * (1 + reps / 30)


def main():
    today = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today()
    P = program()
    order = ["upper", "lowerA", "push", "pull", "legsB"]
    sessions = sorted([s for s in load("sessions") if s.get("type") != "sport"], key=lambda s: s["date"])
    nutrition = sorted(load("nutrition"), key=lambda n: n["date"])
    bw = sorted([b for b in load("bodyweight") if b.get("weight")], key=lambda b: b["date"])
    tgt = {"kcal": 3300, "protein": 170, "carbs": 475, "fat": 80, "sessions": 5, "sleep": 7.5}
    tf = DB / "settings" / "targets.json"
    if tf.exists():
        tgt.update(json.loads(tf.read_text()))

    start = dt.date.fromisoformat(P["start"])
    week = (today - start).days // 7 + 1
    mon = monday(today)
    print(f"BRIEFING  {today:%a %d %b %Y}  ·  {P['block']} \"{P['title']}\" week {week} of {P['weeks']}")

    # ---- bodyweight ----
    print("\nBODYWEIGHT")
    if bw:
        vals = [(dt.date.fromisoformat(b["date"]), b["weight"]) for b in bw]
        last_d, last_w = vals[-1]
        win = [w for d, w in vals if last_d - d <= dt.timedelta(days=6)]
        avg = sum(win) / len(win)
        print(f"  last {last_w:.2f} kg ({last_d:%a %d %b}) · {len(win)}-day avg {avg:.2f} kg "
              f"· {len(vals)} readings since {vals[0][0]:%d %b}")
        prev = [w for d, w in vals if last_d - d > dt.timedelta(days=6) and last_d - d <= dt.timedelta(days=13)]
        if prev:
            delta = avg - sum(prev) / len(prev)
            rate = delta / last_w * 100
            verdict = "on target" if 0.2 <= rate <= 0.4 else ("too fast, mostly fat" if rate > 0.4 else "too slow, add calories")
            print(f"  vs last week {delta:+.2f} kg ({rate:+.2f} % of bodyweight) — {verdict}")
        else:
            print("  weekly trend needs 8+ days of readings")
        if today.weekday() == 6:
            print("  SUNDAY: take the waist measurement at the navel")
    else:
        print("  no readings")

    # ---- this week ----
    wk_s = [s for s in sessions if mon <= dt.date.fromisoformat(s["date"]) <= mon + dt.timedelta(days=6)]
    wk_n = [n for n in nutrition if mon <= dt.date.fromisoformat(n["date"]) <= mon + dt.timedelta(days=6)]
    print(f"\nTHIS WEEK (from Mon {mon:%d %b})")
    print(f"  sessions {len(wk_s)}/{tgt['sessions']}: " + (", ".join(f"{dt.date.fromisoformat(s['date']):%a} {s['name']}" for s in wk_s) or "none yet"))
    sets_by_m = defaultdict(int)
    for s in wk_s:
        for ex in s.get("exercises", []):
            done = sum(1 for t in ex.get("sets", []) if t.get("reps"))
            for m in MUSCLES.get(ex["k"], []):
                sets_by_m[m] += done
    if sets_by_m:
        print("  hard sets per muscle (weekly target in brackets):")
        for m, n in sorted(sets_by_m.items(), key=lambda x: -x[1]):
            lo, hi = TARGET_SETS.get(m, (0, 99))
            mark = "OK " if lo <= n <= hi else ("LOW" if n < lo else "HIGH")
            print(f"    {mark} {m:<12} {n:>2}   [{lo}-{hi}]")
        missing = [m for m in TARGET_SETS if m not in sets_by_m]
        if missing:
            print(f"    NOT TRAINED YET: {', '.join(sorted(missing))}")
    if wk_n:
        n = len(wk_n)
        avg = {k: sum(x.get(k, 0) for x in wk_n) / n for k in ("kcal", "protein", "carbs", "fat")}
        print(f"  food, {n} day(s) logged, daily average:")
        for k, unit in (("kcal", ""), ("protein", " g"), ("carbs", " g"), ("fat", " g")):
            d = avg[k] - tgt[k]
            print(f"    {k:<8} {avg[k]:>6.0f}{unit}  target {tgt[k]}{unit}  {d:+.0f}")

    # ---- last 10 days of food ----
    if nutrition:
        print("\nFOOD, LAST 10 DAYS")
        print("    date          kcal    P    C    F   meals")
        for x in nutrition[-10:]:
            d = dt.date.fromisoformat(x["date"])
            print(f"    {d:%a %d %b}  {x.get('kcal',0):>6.0f} {x.get('protein',0):>4.0f} "
                  f"{x.get('carbs',0):>4.0f} {x.get('fat',0):>4.0f}   {len(x.get('meals',[]))}")

    # ---- exercise board ----
    print("\nEXERCISE BOARD  (last performance → what to prescribe next)")
    lastperf = {}
    for s in sessions:
        for ex in s.get("exercises", []):
            done = [t for t in ex.get("sets", []) if t.get("reps")]
            if done:
                lastperf[ex["k"]] = (s["date"], ex.get("n", ex["k"]), done, ex.get("note", ""))
    for key in order:
        day = P["days"][key]
        rows = []
        for ex in day["ex"]:
            lp = lastperf.get(ex["k"])
            if not lp:
                rows.append((ex["n"], "—", f"start {ex.get('start','test')}"))
                continue
            date, _, done, _note = lp
            lo, hi = ex["reps"]
            # Working load = the heaviest load actually handled, not the last set. He ramps
            # down when tired; the last set would throw the real work away.
            scored = [t for t in done if t.get("load") is not None]
            near = [t for t in scored if t["reps"] >= lo - 2]
            base = max(t["load"] for t in (near or scored)) if scored else None
            all_top = len(done) >= ex["sets"] and all(t["reps"] >= hi for t in done)
            if ex.get("bw") or base is None or (ex.get("added") and not base):
                nxt = "bodyweight, beat the reps"
            elif ex.get("added"):
                nxt = f"+{base:g} kg, beat the reps"
            elif ex.get("prog") == "session":
                nxt = f"{base + ex['inc']:g} kg (+{ex['inc']:g} every session)"
            elif all_top:
                nxt = f"{base + ex['inc']:g} kg (+{ex['inc']:g}, hit the top last time)"
            else:
                nxt = f"{base:g} kg, beat the reps"
            rows.append((ex["n"], f"{fmt_sets(done, ex.get('added', False))}  ({date[5:]})", nxt))
        print(f"\n  {day['name']}")
        for n, last, nxt in rows:
            print(f"    {n[:44]:<44} {last:<34} → {nxt}")

    # ---- patterns the data reveals ----
    # ---- personal bests, straight from the flat table ----
    print("\nPERSONAL BESTS (heaviest load handled, and best estimated 1RM)")
    best = {}
    for s_ in sessions:
        for ex in s_.get("exercises", []):
            for t in ex.get("sets", []):
                if not t.get("reps") or t.get("load") is None:
                    continue
                k = ex["k"]
                cur = best.get(k)
                v = e1rm(t["load"], t["reps"])
                if not cur or v > cur[0]:
                    best[k] = (v, t["load"], t["reps"], s_["date"], ex.get("n", k))
    for k, (v, ld, rp, d, n) in sorted(best.items(), key=lambda x: -x[1][0]):
        print(f"    {n[:44]:<44} {ld:g}×{rp:g} on {d[5:]}   e1RM {v:.0f} kg")

    print("\nPATTERNS IN THE DATA")
    flags = []
    light_first, rounds, no_rir, total_sets = [], [], 0, 0
    for s in sessions:
        for ex in s.get("exercises", []):
            done = [t for t in ex.get("sets", []) if t.get("reps")]
            total_sets += len(done)
            no_rir += sum(1 for t in done if t.get("rir") is None)
            loads = [t.get("load") for t in done if t.get("load") is not None]
            if len(loads) >= 2 and loads[0] < max(loads[1:]):
                light_first.append(f"{s['date'][5:]} {ex.get('n','?')[:28]}: {loads[0]:g} → {max(loads[1:]):g}")
            reps = [t["reps"] for t in done]
            if len(reps) >= 3 and len(set(reps)) == 1:
                rounds.append(f"{s['date'][5:]} {ex.get('n','?')[:28]}: {len(reps)}× {reps[0]:g} reps")
    if light_first:
        flags.append(f"First set too light, {len(light_first)} time(s) — the opener is being used as a warm-up:")
        flags += [f"    {x}" for x in light_first]
    if rounds:
        flags.append(f"Every set on the same round number, {len(rounds)} time(s) — sets ended in the head, not the muscle:")
        flags += [f"    {x}" for x in rounds]
    if total_sets:
        flags.append(f"RIR missing on {no_rir}/{total_sets} sets ({no_rir/total_sets*100:.0f} %) — ask in the same message as the next set.")
    fat_over = [x["date"][5:] for x in nutrition if x.get("fat", 0) > tgt["fat"]]
    carb_short = [x["date"][5:] for x in nutrition if x.get("carbs", 0) < tgt["carbs"] * 0.8]
    prot_short = [x["date"][5:] for x in nutrition if x.get("protein", 0) < tgt["protein"] * 0.9]
    if fat_over:
        flags.append(f"Fat over target on {len(fat_over)}/{len(nutrition)} days: {', '.join(fat_over)}")
    if carb_short:
        flags.append(f"Carbs under 80 % of target on {len(carb_short)}/{len(nutrition)} days: {', '.join(carb_short)}")
    if prot_short:
        flags.append(f"Protein under 90 % of target on: {', '.join(prot_short)}")
    slept = [(s["date"][5:], s["sleep"]) for s in sessions if s.get("sleep")]
    flags.append("Sleep logged on " + (", ".join(f"{d} {v:g} h" for d, v in slept) if slept else "no session yet — ask every morning."))
    for f in flags:
        print("  " + f if not f.startswith("    ") else f)

    # ---- facts that must never be forgotten ----
    ff = ROOT / "data" / "facts.json"
    if ff.exists():
        F = json.loads(ff.read_text())
        print("\nFACTS (data/facts.json)")
        u = F.get("units", {})
        print(f"  bowl = {u.get('bowl_ml')} ml · 1 tbsp PB {u.get('tablespoon_peanut_butter_g')} g · 1 tbsp honey {u.get('tablespoon_honey_g')} g · glass {u.get('glass_ml')} ml · rice bag {u.get('rice_bag_dry_g')} g dry")
        print(f"  pull-ups in added kg · Hammer press per side · dumbbells per hand · machines stack kg")
        print(f"  progression: {F.get('progression',{}).get('working_load','')}")
        th = F.get("training_habits", {})
        if th:
            print(f"  trains {th.get('weekday_session_time','?')} · partials → {th.get('reports_partials_as','')}")
        print(f"  likes: {', '.join(F.get('likes', [])[:8])}")
        print(f"  refuses: {', '.join(F.get('refuses', []))}")
        sp = F.get("shopping", {})
        if sp.get("outstanding"):
            print(f"  still to buy: {', '.join(sp['outstanding'])}")
        for q in F.get("open_questions", []):
            print(f"  open: {q}")

    # ---- what is next ----
    idx = order.index(sessions[-1]["dayKey"]) if sessions and sessions[-1]["dayKey"] in order else -1
    nxt = order[(idx + 1) % len(order)]
    done_today = any(s["date"] == today.isoformat() for s in sessions)
    print(f"\nNEXT SESSION: {P['days'][nxt]['name']} — {'tomorrow, today is done' if done_today else 'today'}"
          f" ({len(P['days'][nxt]['ex'])} exercises)")
    print("Read profile/patterns.md before prescribing anything.")


if __name__ == "__main__":
    main()

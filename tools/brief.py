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
    # A set counts 1.0 for the muscle the exercise is chosen for, 0.5 for a muscle that only
    # assists. Counting a chest press as a full triceps set is what put triceps at 24 sets in
    # week 1 and made the briefing demand a cut that was not real.
    "bench": {"chest": 1, "triceps": 0.5}, "incdb": {"chest": 1, "triceps": 0.5},
    "dips": {"chest": 1, "triceps": 0.5}, "pecdeck": {"chest": 1}, "cablefly": {"chest": 1},
    "csrow": {"back": 1, "biceps": 0.5}, "dbrow": {"back": 1, "biceps": 0.5},
    "tbarrow": {"back": 1, "biceps": 0.5}, "cablerow": {"back": 1, "biceps": 0.5},
    "pullup": {"back": 1, "biceps": 0.5}, "sapd": {"back": 1}, "revpec": {"rear delts": 1},
    "ohp": {"shoulders": 1, "triceps": 0.5}, "dbohp": {"shoulders": 1, "triceps": 0.5},
    "dblat": {"side delts": 1},
    "ezcurl": {"biceps": 1}, "inccurl": {"biceps": 1}, "hammer": {"biceps": 1},
    "pushdown": {"triceps": 1}, "ohtri": {"triceps": 1},
    "squat": {"quads": 1, "glutes": 0.5}, "legpress": {"quads": 1, "glutes": 0.5},
    "lunge": {"quads": 1, "glutes": 1}, "bss": {"quads": 1, "glutes": 1}, "legext": {"quads": 1},
    "rdl": {"hamstrings": 1, "glutes": 1},
    "trapbar": {"hamstrings": 0.5, "glutes": 1, "quads": 0.5, "back": 0.5},
    "legcurl": {"hamstrings": 1}, "nordic": {"hamstrings": 1},
    "hanglr": {"abs": 1}, "abwheel": {"abs": 1}, "copenhagen": {"abs": 1}, "landing": {},
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


DEFAULT_GYM = "fitnesspark"
GYM_NAMES = {"fitnesspark": "Fitness Park", "campus": "SKEMA campus"}


def last_by_gym(sessions):
    """Last performance of every exercise, kept separately per gym.

    Stack numbers do not transfer between gyms: the campus Kinesis "level 15" is not 15 kg,
    and the campus Technogym leg press is not the Nautilus. Mixing them once prescribed a
    15 kg Romanian deadlift for a man who pulls 50. Never merge the two gyms again.
    """
    out = defaultdict(dict)
    for s in sessions:
        g = s.get("gym", DEFAULT_GYM)
        for ex in s.get("exercises", []):
            done = [t for t in ex.get("sets", []) if t.get("reps")]
            if done:
                out[ex["k"]][g] = (s["date"], ex.get("n", ex["k"]), done, ex.get("note", ""))
    return out


def pick_gym(by_gym, gym=DEFAULT_GYM):
    """The record to prescribe from: this gym\'s, else the newest elsewhere, flagged as such."""
    if gym in by_gym:
        return by_gym[gym], True
    if not by_gym:
        return None, True
    return max(by_gym.values(), key=lambda x: x[0]), False


def prescribe(ex, lp, ov=None):
    """(load text, last-performance text) for one exercise, from its last session at this gym.

    `ov` is a coach override from data/facts.json: a load the athlete has proven he can handle
    but did not use last time (he under-loads an exercise for a whole session now and then).
    """
    if not lp:
        st = ov["load"] if ov else ex.get("start", "test")
        return f"start {st}", "—"
    date, _n, done, _note = lp
    lo, hi = ex["reps"]
    # Working load = the heaviest load actually handled, not the last set. He ramps down when
    # tired; reading the last set throws the real work away.
    scored = [t for t in done if t.get("load") is not None]
    near = [t for t in scored if t["reps"] >= lo - 2]
    base = max(t["load"] for t in (near or scored)) if scored else None
    all_top = len(done) >= ex["sets"] and all(t["reps"] >= hi for t in done)
    if ov and base is not None and ov["load"] > base:
        return f"{ov['load']:g} kg — {ov['why']}", f"{fmt_sets(done, ex.get('added', False))}  ({date[5:]})"
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
    return nxt, f"{fmt_sets(done, ex.get('added', False))}  ({date[5:]})"


def main():
    # The athlete lives in France. The container runs on UTC - never reason about "now" from
    # message flow, read the clock in his timezone.
    import os, time
    FOOD = "--food" in sys.argv or "--all" in sys.argv
    os.environ["TZ"] = "Europe/Paris"; time.tzset()
    now = dt.datetime.now()
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    today = dt.date.fromisoformat(args[0]) if args else now.date()
    P = program()
    OV = json.loads((ROOT / "data" / "facts.json").read_text()).get("coach_overrides", {}) \
        if (ROOT / "data" / "facts.json").exists() else {}
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
    print(f"BRIEFING  {today:%a %d %b %Y}  ·  local time now {now:%H:%M} (Europe/Paris)  ·  {P['block']} \"{P['title']}\" week {week} of {P['weeks']}")

    # ---- what to train today: the first thing a coach needs ----
    lp_all = last_by_gym(sessions)
    idx = order.index(sessions[-1]["dayKey"]) if sessions and sessions[-1]["dayKey"] in order else -1
    nxt = order[(idx + 1) % len(order)]
    done_today = any(s["date"] == today.isoformat() for s in sessions)
    day = P["days"][nxt]
    hdr = "NEXT SESSION (today is already logged)" if done_today else "TRAIN TODAY"
    print(f"\n{hdr}: {day['name']} — {day['sub']} · {len(day['ex'])} exercises · "
          f"{sum(e['sets'] for e in day['ex'])} sets")
    print(f"    {'exercise':<42} {'sets × reps':<15} {'prescribe':<30} last time")
    for ex in day["ex"]:
        lp, same = pick_gym(lp_all.get(ex["k"], {}))
        nl, lastt = prescribe(ex, lp, OV.get(ex["k"]))
        reps = f"{ex['sets']} × {ex['reps'][0]:g}-{ex['reps'][1]:g}" + (" /side" if ex.get("perSide") else "")
        print(f"    {ex['n'][:42]:<42} {reps:<15} {nl[:30]:<30} {lastt}" + ("" if same else "  [OTHER GYM]"))

    # ---- this week ----
    wk_s = [s for s in sessions if mon <= dt.date.fromisoformat(s["date"]) <= mon + dt.timedelta(days=6)]
    wk_n = [n for n in nutrition if mon <= dt.date.fromisoformat(n["date"]) <= mon + dt.timedelta(days=6)]
    print(f"\nTHIS WEEK (from Mon {mon:%d %b})")
    print(f"  sessions {len(wk_s)}/{tgt['sessions']}: " + (", ".join(f"{dt.date.fromisoformat(s['date']):%a} {s['name']}" for s in wk_s) or "none yet"))
    sets_by_m = defaultdict(int)
    for s in wk_s:
        for ex in s.get("exercises", []):
            done = sum(1 for t in ex.get("sets", []) if t.get("reps"))
            for m, w in MUSCLES.get(ex["k"], {}).items():
                sets_by_m[m] += done * w
    if sets_by_m:
        print("  HARD SETS PER MUSCLE (weekly target in brackets):")
        for m, n in sorted(sets_by_m.items(), key=lambda x: -x[1]):
            lo, hi = TARGET_SETS.get(m, (0, 99))
            mark = "OK " if lo <= n <= hi else ("LOW" if n < lo else "HIGH")
            print(f"    {mark} {m:<12} {n:>4.1f}   [{lo}-{hi}]")
        missing = [m for m in TARGET_SETS if m not in sets_by_m]
        if missing:
            print(f"    NOT TRAINED YET: {', '.join(sorted(missing))}")
    if wk_n:
        n = len(wk_n)
        avg = {k: sum(x.get(k, 0) for x in wk_n) / n for k in ("kcal", "protein", "carbs", "fat")}
        if FOOD:
            print(f"  food, {n} day(s) logged, daily average:")
            for k, unit in (("kcal", ""), ("protein", " g"), ("carbs", " g"), ("fat", " g")):
                d = avg[k] - tgt[k]
                print(f"    {k:<8} {avg[k]:>6.0f}{unit}  target {tgt[k]}{unit}  {d:+.0f}")
        else:
            print(f"  food (not the focus - he asked for training only): {n} day(s) logged, "
                  f"{avg['kcal']:.0f} kcal / {avg['protein']:.0f} g protein per day. "
                  f"Run `brief.py --food` when he brings food up.")

    # ---- exercise board ----
    print("\nEXERCISE BOARD  (last performance at each gym → what to prescribe next)")
    for key in order:
        day = P["days"][key]
        print(f"\n  {day['name']}")
        for ex in day["ex"]:
            by_gym = lp_all.get(ex["k"], {})
            lp, same = pick_gym(by_gym)
            nxt_, last_ = prescribe(ex, lp, OV.get(ex["k"]))
            print(f"    {ex['n'][:42]:<42} {last_:<34} -> {nxt_}" + ("" if same else "  [OTHER GYM]"))
            for g, rec in by_gym.items():
                if lp and g != (DEFAULT_GYM if same else None) and rec is not lp:
                    print(f"      {GYM_NAMES.get(g, g)}: {fmt_sets(rec[2], ex.get('added', False))}  ({rec[0][5:]})"
                          f" — stack numbers do not transfer")

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
    if fat_over and FOOD:
        flags.append(f"Fat over target on {len(fat_over)}/{len(nutrition)} days: {', '.join(fat_over)}")
    if carb_short and FOOD:
        flags.append(f"Carbs under 80 % of target on {len(carb_short)}/{len(nutrition)} days: {', '.join(carb_short)}")
    if prot_short and FOOD:
        flags.append(f"Protein under 90 % of target on: {', '.join(prot_short)}")
    slept = [(s["date"][5:], s["sleep"]) for s in sessions if s.get("sleep")]
    flags.append("Sleep logged on " + (", ".join(f"{d} {v:g} h" for d, v in slept) if slept else "no session yet — ask every morning."))
    for f in flags:
        print("  " + f if not f.startswith("    ") else f)

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

    # ---- last 10 days of food ----
    if nutrition and FOOD:
        print("\nFOOD, LAST 10 DAYS")
        print("    date          kcal    P    C    F   meals")
        for x in nutrition[-10:]:
            d = dt.date.fromisoformat(x["date"])
            print(f"    {d:%a %d %b}  {x.get('kcal',0):>6.0f} {x.get('protein',0):>4.0f} "
                  f"{x.get('carbs',0):>4.0f} {x.get('fat',0):>4.0f}   {len(x.get('meals',[]))}")

    # ---- university timetable: today and tomorrow ----
    tf = ROOT / "data" / "timetable.json"
    if tf.exists():
        T = json.loads(tf.read_text())
        DAYS = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
        def day_line(d):
            name = DAYS[d.weekday()]; iso = d.isoformat()
            ex = [e for e in T.get("exceptions", []) if e["from"] <= iso <= e.get("to", e["from"])]
            first, last = T["term"]["first_class"], T["term"]["last_class"]
            cls = T["weekly"].get(name, []) if first <= iso <= last else []
            cls = [c for c in cls if c["first"] <= iso <= c["last"]]
            one = [o for o in T.get("one_off_sessions", []) if o["date"] == iso]
            parts = []
            for c in cls + one:
                parts.append(f"{c['start']}–{c['end']} {c['course'].title()[:28]} ({'online' if c['mode']=='online' else 'campus'})")
            tag = "; ".join(e["title"] for e in ex)
            w = T["training_windows"].get(name, {})
            print(f"  {d:%a %d %b}: " + (", ".join(parts) if parts else "no classes") + (f"  [{tag}]" if tag else ""))
            print(f"    train: {w.get('best','?')}  — {w.get('why','')}")
            print(f"    food:  {T['meal_logistics'].get(name,'')}")
        print("\nUNIVERSITY (data/timetable.json)")
        day_line(today); day_line(today + dt.timedelta(days=1))

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


    print("\nRead profile/patterns.md before prescribing anything.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Class timetable → training windows.

Reads the athlete's calendar exports (`data/schedule/*.ics`, from Calendar.app
File > Export, or any .ics) plus an optional hand-typed `data/schedule/manual.csv`,
expands recurring events, classifies every class as in-person or online, and
writes:

  data/schedule/classes.json   every class occurrence in the window (machine-readable)
  profile/schedule.md          the typical week, the next two weeks day by day, and
                               the training window per weekday (coach-readable)

Usage:  python3 tools/schedule.py [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--tz Europe/Paris]
        python3 tools/schedule.py --week [YYYY-MM-DD]   # print one week from classes.json

Classification: online if the location, URL or description mentions a video
platform or online/distanciel wording; in person if there is a physical location;
unknown otherwise. `data/schedule/overrides.json` ({"title substring": "online" |
"in-person" | "ignore"}) wins over the heuristic. Events matching "ignore" (or the
IGNORE words below: gym, training, birthday, ...) are dropped so only classes and
fixed commitments remain.

manual.csv columns: weekday,start,end,title,mode,location   (weekday Mon..Sun,
times HH:MM, mode online|in-person). Each row is a weekly class for the window.
"""
import argparse, csv, json, re, sys, datetime as dt
from collections import defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from dateutil import rrule as _rr
except ImportError:  # pragma: no cover
    _rr = None

ROOT = Path(__file__).resolve().parent.parent
SDIR = ROOT / "data" / "schedule"
OUT_JSON = SDIR / "classes.json"
OUT_MD = ROOT / "profile" / "schedule.md"

ONLINE_WORDS = ["zoom", "teams", "meet.google", "google meet", "webex", "skype", "http://", "https://",
                "online", "visio", "distanciel", "en ligne", "à distance", "a distance", "virtual",
                "remote", "bbb", "bigbluebutton", "moodle", "livestream", "webinar"]
IGNORE_WORDS = ["gym", "training", "workout", "muscu", "boxing", "padel", "basket", "birthday",
                "anniversaire", "geburtstag", "holiday", "férié", "feiertag"]
WD = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
USUAL_SLOT = (dt.time(19, 30), dt.time(21, 0))   # from data/facts.json training_habits
MIN_GAP_MIN = 90                                # a lifting session plus travel


# ---------------------------------------------------------------- ICS parsing
def unfold(text):
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []
    for ln in lines:
        if ln[:1] in (" ", "\t") and out:
            out[-1] += ln[1:]
        else:
            out.append(ln)
    return out


_PROP = re.compile(r'^([A-Za-z0-9-]+)((?:;[A-Za-z0-9-]+=(?:"[^"]*"|[^;:]*))*):(.*)$')


def parse_line(ln):
    m = _PROP.match(ln)
    if not m:
        return None, {}, ln
    name, raw_params, value = m.group(1).upper(), m.group(2), m.group(3)
    params = {}
    for p in re.findall(r';([A-Za-z0-9-]+)=("[^"]*"|[^;:]*)', raw_params):
        params[p[0].upper()] = p[1].strip('"')
    return name, params, value


def unescape(v):
    return v.replace("\\n", "\n").replace("\\N", "\n").replace("\\,", ",").replace("\\;", ";").replace("\\\\", "\\")


def parse_dt(value, params, tz):
    """→ (naive datetime in tz, all_day)"""
    value = value.strip()
    if params.get("VALUE") == "DATE" or (len(value) == 8 and value.isdigit()):
        return dt.datetime.strptime(value, "%Y%m%d"), True
    if value.endswith("Z"):
        d = dt.datetime.strptime(value[:-1], "%Y%m%dT%H%M%S").replace(tzinfo=dt.timezone.utc)
        return d.astimezone(tz).replace(tzinfo=None), False
    d = dt.datetime.strptime(value[:15], "%Y%m%dT%H%M%S")
    tzid = params.get("TZID")
    if tzid:
        try:
            src = ZoneInfo(tzid)
            d = d.replace(tzinfo=src).astimezone(tz).replace(tzinfo=None)
        except Exception:
            pass  # unknown zone name: treat as already local
    return d, False


def parse_duration(v):
    m = re.match(r"^(-?)P(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$", v.strip())
    if not m:
        return dt.timedelta(hours=1)
    sign = -1 if m.group(1) else 1
    w, d, h, mi, s = (int(x) if x else 0 for x in m.groups()[1:])
    return sign * dt.timedelta(weeks=w, days=d, hours=h, minutes=mi, seconds=s)


def read_ics(path, tz):
    """→ list of raw event dicts (masters and overrides), calendar name."""
    events, cur, calname = [], None, path.stem
    depth_other = 0
    for ln in unfold(path.read_text(encoding="utf-8", errors="replace")):
        name, params, value = parse_line(ln)
        if name == "BEGIN":
            if value.upper() == "VEVENT":
                cur = {"exdates": set(), "src": path.name}
            elif cur is not None:
                depth_other += 1
            continue
        if name == "END":
            if value.upper() == "VEVENT" and cur is not None:
                events.append(cur); cur = None
            elif cur is not None and depth_other:
                depth_other -= 1
            continue
        if cur is None:
            if name == "X-WR-CALNAME":
                calname = unescape(value)
            continue
        if depth_other:
            continue  # inside VALARM etc.
        if name in ("DTSTART", "DTEND", "RECURRENCE-ID"):
            cur[name], cur[name + "_ALLDAY"] = parse_dt(value, params, tz)
        elif name == "EXDATE":
            for v in value.split(","):
                cur["exdates"].add(parse_dt(v, params, tz)[0])
        elif name in ("SUMMARY", "LOCATION", "DESCRIPTION", "URL", "UID", "RRULE", "DURATION", "STATUS"):
            cur[name] = unescape(value) if name != "RRULE" else value
    for e in events:
        e["calendar"] = calname
    return events, calname


def expand(ev, start, end, tz):
    """Occurrences of one raw event as (begin, finish, all_day) naive local."""
    if "DTSTART" not in ev:
        return []
    s = ev["DTSTART"]
    all_day = ev.get("DTSTART_ALLDAY", False)
    if "DTEND" in ev:
        dur = ev["DTEND"] - s
    elif "DURATION" in ev:
        dur = parse_duration(ev["DURATION"])
    else:
        dur = dt.timedelta(days=1) if all_day else dt.timedelta(hours=1)
    rule = ev.get("RRULE")
    if not rule:
        return [(s, s + dur, all_day)] if s < end and s + dur > start else []
    if _rr is None:
        print("  ! python-dateutil missing, cannot expand RRULE for", ev.get("SUMMARY"), file=sys.stderr)
        return [(s, s + dur, all_day)]
    # UNTIL may be in UTC ("...Z"); dateutil wants it to match the naive dtstart.
    def fix_until(m):
        v = m.group(1)
        if v.endswith("Z"):
            u = dt.datetime.strptime(v[:-1], "%Y%m%dT%H%M%S").replace(tzinfo=dt.timezone.utc)
            v = u.astimezone(tz).strftime("%Y%m%dT%H%M%S")
        elif len(v) == 8:
            v += "T235959"
        return "UNTIL=" + v
    rule = re.sub(r"UNTIL=([0-9TZ]+)", fix_until, rule)
    try:
        rr = _rr.rrulestr(rule, dtstart=s)
    except Exception as ex:
        print(f"  ! cannot parse RRULE '{rule}' for {ev.get('SUMMARY')}: {ex}", file=sys.stderr)
        return [(s, s + dur, all_day)]
    out = []
    for b in rr.between(start - dur, end, inc=True):
        if b in ev["exdates"] or (all_day and b.date() in {x.date() for x in ev["exdates"]}):
            continue
        out.append((b, b + dur, all_day))
        if len(out) > 400:
            break
    return out


# ---------------------------------------------------------------- classification
def load_overrides():
    p = SDIR / "overrides.json"
    return json.loads(p.read_text()) if p.exists() else {}


def classify(title, location, desc, url, overrides):
    t = (title or "").lower()
    for k, v in overrides.items():
        if k.lower() in t:
            return v
    blob = " ".join(x or "" for x in (title, location, desc, url)).lower()
    if any(w in t for w in IGNORE_WORDS):
        return "ignore"
    if any(w in blob for w in ONLINE_WORDS):
        return "online"
    if (location or "").strip():
        return "in-person"
    return "unknown"


# ---------------------------------------------------------------- build
def build(start, end, tz):
    overrides = load_overrides()
    occ = []
    files = sorted(SDIR.glob("*.ics"))
    for f in files:
        events, cal = read_ics(f, tz)
        by_uid = defaultdict(lambda: {"master": None, "overrides": []})
        for e in events:
            uid = e.get("UID", id(e))
            if "RECURRENCE-ID" in e:
                by_uid[uid]["overrides"].append(e)
            else:
                by_uid[uid]["master"] = e
        n_file = 0
        for uid, grp in by_uid.items():
            moved = {o["RECURRENCE-ID"] for o in grp["overrides"]}
            items = []
            if grp["master"]:
                items += [(grp["master"], b, f_, ad) for b, f_, ad in expand(grp["master"], start, end, tz)
                          if b not in moved]
            for o in grp["overrides"]:
                if o.get("STATUS", "").upper() == "CANCELLED":
                    continue
                items += [(o, b, f_, ad) for b, f_, ad in expand(o, start, end, tz)]
            for e, b, f_, ad in items:
                if e.get("STATUS", "").upper() == "CANCELLED":
                    continue
                mode = classify(e.get("SUMMARY"), e.get("LOCATION"), e.get("DESCRIPTION"), e.get("URL"), overrides)
                if mode == "ignore":
                    continue
                if ad and mode == "unknown":
                    mode = "all-day"
                occ.append({"date": b.date().isoformat(), "start": b.strftime("%H:%M"), "end": f_.strftime("%H:%M"),
                            "all_day": ad, "title": (e.get("SUMMARY") or "(no title)").strip(),
                            "mode": mode, "location": (e.get("LOCATION") or "").strip().replace("\n", ", "),
                            "calendar": cal, "uid": str(uid), "source": f.name})
                n_file += 1
        print(f"  {f.name}: {len(events)} events → {n_file} class occurrences in window")
    man = SDIR / "manual.csv"
    if man.exists():
        n = 0
        with man.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                wd = WD.index(row["weekday"].strip()[:3].title())
                d = start.date() + dt.timedelta(days=(wd - start.weekday()) % 7)
                while d < end.date():
                    occ.append({"date": d.isoformat(), "start": row["start"].strip(), "end": row["end"].strip(),
                                "all_day": False, "title": row["title"].strip(),
                                "mode": (row.get("mode") or "unknown").strip(), "location": (row.get("location") or "").strip(),
                                "calendar": "manual.csv", "uid": f"manual-{wd}-{row['start']}-{row['title']}", "source": "manual.csv"})
                    d += dt.timedelta(days=7); n += 1
        print(f"  manual.csv: {n} occurrences")
    # de-duplicate (same class exported from two calendars)
    seen, uniq = set(), []
    for o in sorted(occ, key=lambda o: (o["date"], o["start"], o["title"])):
        k = (o["date"], o["start"], o["end"], o["title"].lower())
        if k not in seen:
            seen.add(k); uniq.append(o)
    return uniq


# ---------------------------------------------------------------- analysis
def tmin(s):
    h, m = s.split(":"); return int(h) * 60 + int(m)


def tstr(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def typical_week(occ, weeks):
    """Group timed occurrences by weekday/time/title; keep the ones that repeat."""
    g = defaultdict(list)
    for o in occ:
        if o["all_day"]:
            continue
        wd = dt.date.fromisoformat(o["date"]).weekday()
        g[(wd, o["start"], o["end"], o["title"], o["mode"])].append(o)
    typ, once = {}, []
    for k, items in g.items():
        if len(items) >= 2 or len(items) >= max(1, weeks // 2):
            typ[k] = items
        else:
            once += items
    return typ, once


def day_windows(blocks):
    """blocks: list of (start_min, end_min, mode). → analysis dict for one weekday."""
    if not blocks:
        return {"free": "all day", "first": None, "last": None, "usual_ok": True, "gap": None, "inperson": 0}
    blocks = sorted(blocks)
    first, last = blocks[0][0], max(b[1] for b in blocks)
    us, ue = tmin(USUAL_SLOT[0].strftime("%H:%M")), tmin(USUAL_SLOT[1].strftime("%H:%M"))
    usual_ok = all(b[1] <= us or b[0] >= ue for b in blocks)
    # longest free gap between 08:00 and 22:00
    edges = [(480, 480)] + [(b[0], b[1]) for b in blocks] + [(1320, 1320)]
    gap, cur_end = None, 480
    for s, e in edges:
        if s - cur_end >= MIN_GAP_MIN and (gap is None or s - cur_end > gap[1] - gap[0]):
            gap = (cur_end, s)
        cur_end = max(cur_end, e)
    return {"first": tstr(first), "last": tstr(last), "usual_ok": usual_ok,
            "gap": f"{tstr(gap[0])}–{tstr(gap[1])}" if gap else None,
            "inperson": sum(1 for b in blocks if b[2] == "in-person"),
            "free": f"from {tstr(last)}"}


def write_md(occ, start, end, tz):
    weeks = max(1, (end.date() - start.date()).days // 7)
    typ, once = typical_week(occ, weeks)
    today = dt.date.today()
    L = ["# Class schedule (generated, do not edit by hand)", "",
         f"Generated {today.isoformat()} by `tools/schedule.py` from `data/schedule/` "
         f"(window {start.date()} to {end.date()}, timezone {tz.key}).",
         "Re-run the tool after a new calendar export. Overrides live in `data/schedule/overrides.json`.", ""]
    if not occ:
        L += ["No classes found. Export the calendar from Calendar.app (File > Export > Export…) into",
              "`data/schedule/` or fill `data/schedule/manual.csv`, then run `python3 tools/schedule.py`.", ""]
        OUT_MD.write_text("\n".join(L)); return
    # typical week
    L += ["## Typical week", "", "| Day | Time | Class | Mode | Where | Seen |", "|---|---|---|---|---|---|"]
    per_day = defaultdict(list)
    for (wd, s, e, t, mode), items in sorted(typ.items()):
        loc = next((i["location"] for i in items if i["location"]), "")
        L.append(f"| {WD[wd]} | {s}–{e} | {t} | {mode} | {loc} | {len(items)}× |")
        per_day[wd].append((tmin(s), tmin(e), mode))
    L += ["", "## Training windows per weekday", "",
          f"Usual lifting slot {USUAL_SLOT[0]:%H:%M}–{USUAL_SLOT[1]:%H:%M} (data/facts.json). "
          f"A window needs at least {MIN_GAP_MIN} min.", "",
          "| Day | Classes | First | Last | In person | Usual slot free | Longest daytime gap |",
          "|---|---|---|---|---|---|---|"]
    for wd in range(7):
        a = day_windows(per_day.get(wd, []))
        n = len(per_day.get(wd, []))
        L.append(f"| {WD[wd]} | {n} | {a['first'] or '—'} | {a['last'] or '—'} | {a['inperson']} | "
                 f"{'yes' if a['usual_ok'] else 'NO'} | {a['gap'] or ('all day' if not n else '—')} |")
    # coach notes computed from the table
    notes = []
    heavy = [WD[wd] for wd in range(7) if sum(e - s for s, e, _ in per_day.get(wd, [])) >= 6 * 60]
    if heavy:
        notes.append(f"Long class days (6 h+): {', '.join(heavy)}. Expect low energy and a late, short meal history; push food earlier.")
    late = [WD[wd] for wd in range(7) if per_day.get(wd) and max(e for _, e, _ in per_day[wd]) > tmin("19:00")]
    if late:
        notes.append(f"Classes past 19:00 on {', '.join(late)}: the usual evening slot is squeezed, train before class or move the session.")
    early = [WD[wd] for wd in range(7) if per_day.get(wd) and min(s for s, _, _ in per_day[wd]) <= tmin("08:30")]
    if early:
        notes.append(f"Early start (≤08:30) on {', '.join(early)}: a session ending 21:00 the evening before costs sleep. Watch the sleep field on those mornings.")
    free = [WD[wd] for wd in range(5) if not per_day.get(wd)]
    if free:
        notes.append(f"No classes on {', '.join(free)}: best days for the leg sessions and the long meals.")
    online_only = [WD[wd] for wd in range(7) if per_day.get(wd) and all(m == "online" for _, _, m in per_day[wd])]
    if online_only:
        notes.append(f"Online-only days ({', '.join(online_only)}): no commute, steps will be low, cook and eat at home, daytime gym visit possible.")
    if notes:
        L += ["", "Coach notes (auto):"] + [f"- {n}" for n in notes]
    # next two weeks
    L += ["", "## Next two weeks", ""]
    d0 = today - dt.timedelta(days=today.weekday())
    by_date = defaultdict(list)
    for o in occ:
        by_date[o["date"]].append(o)
    for i in range(14):
        d = d0 + dt.timedelta(days=i)
        items = by_date.get(d.isoformat(), [])
        if i in (0, 7):
            L.append(f"### Week of {d.isoformat()}")
        if not items:
            L.append(f"- {WD[d.weekday()]} {d.day:02d}.{d.month:02d}: free")
            continue
        parts = [("all day " if o["all_day"] else f"{o['start']}–{o['end']} ") + f"{o['title']} ({o['mode']})" for o in items]
        L.append(f"- {WD[d.weekday()]} {d.day:02d}.{d.month:02d}: " + "; ".join(parts))
    if once:
        L += ["", "## One-off entries in the window", ""]
        for o in sorted(once, key=lambda o: (o["date"], o["start"]))[:40]:
            L.append(f"- {o['date']} {'all day' if o['all_day'] else o['start'] + '–' + o['end']} {o['title']} ({o['mode']}{', ' + o['location'] if o['location'] else ''})")
    unknown = sorted({o["title"] for o in occ if o["mode"] == "unknown"})
    if unknown:
        L += ["", "## Mode unknown (no location, no link) — ask the athlete, then add to overrides.json", ""]
        L += [f"- {t}" for t in unknown]
    OUT_MD.write_text("\n".join(L) + "\n")


def print_week(day):
    if not OUT_JSON.exists():
        print("no data/schedule/classes.json yet — run tools/schedule.py after adding an export"); return
    occ = json.loads(OUT_JSON.read_text())
    d0 = day - dt.timedelta(days=day.weekday())
    print(f"CLASSES week of {d0}")
    for i in range(7):
        d = (d0 + dt.timedelta(days=i)).isoformat()
        items = [o for o in occ if o["date"] == d]
        if not items:
            print(f"  {WD[i]} {d[5:]}: free"); continue
        blocks = [(tmin(o["start"]), tmin(o["end"]), o["mode"]) for o in items if not o["all_day"]]
        a = day_windows(blocks)
        s = "; ".join(("all day " if o["all_day"] else f"{o['start']}–{o['end']} ") + f"{o['title']} ({o['mode']})" for o in items)
        tail = "" if not blocks else f"  → free {a['free']}, usual slot {'ok' if a['usual_ok'] else 'BLOCKED'}"
        print(f"  {WD[i]} {d[5:]}: {s}{tail}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start"); ap.add_argument("--to", dest="end")
    ap.add_argument("--tz", default="Europe/Paris")
    ap.add_argument("--week", nargs="?", const="today")
    a = ap.parse_args()
    tz = ZoneInfo(a.tz)
    if a.week:
        print_week(dt.date.today() if a.week == "today" else dt.date.fromisoformat(a.week)); return
    today = dt.date.today()
    start = dt.datetime.combine(dt.date.fromisoformat(a.start) if a.start else today - dt.timedelta(days=today.weekday() + 7), dt.time())
    end = dt.datetime.combine(dt.date.fromisoformat(a.end) if a.end else today + dt.timedelta(days=90), dt.time())
    SDIR.mkdir(parents=True, exist_ok=True)
    print(f"Reading {SDIR.relative_to(ROOT)}/ for {start.date()} → {end.date()} ({a.tz})")
    occ = build(start, end, tz)
    OUT_JSON.write_text(json.dumps(occ, indent=1, ensure_ascii=False) + "\n")
    write_md(occ, start, end, tz)
    n_ip = sum(1 for o in occ if o["mode"] == "in-person"); n_on = sum(1 for o in occ if o["mode"] == "online")
    n_un = sum(1 for o in occ if o["mode"] == "unknown")
    print(f"Wrote {len(occ)} occurrences → {OUT_JSON.relative_to(ROOT)} (in person {n_ip}, online {n_on}, unknown {n_un})")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

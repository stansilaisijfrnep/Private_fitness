# data/schedule/ — the athlete's class timetable

Why: training windows, commute days, energy and meal timing all depend on when classes are and
whether they are in person or online. `tools/schedule.py` turns the calendar into
`profile/schedule.md` (coach view) and `classes.json` (used by `tools/brief.py`).

## Getting the calendar in here
Apple Calendar cannot be read from the coaching session directly. Two routes:

1. **Export from Calendar.app (Mac).** Click the uni calendar in the sidebar, then
   File > Export > Export…, save the `.ics` and drop it into this folder (any file name, several
   files are fine, one per calendar). Then run `python3 tools/schedule.py`.
   Re-export at the start of each semester or when the timetable changes.
2. **Google Calendar connector.** If the classes also live in (or sync to) Google Calendar, turn the
   Google Calendar connector on for the chat. The coach then reads the events and writes
   `classes.json` in the same format below, then runs `python3 tools/schedule.py --week`.

Fallback: type the weekly timetable into `manual.csv` with the header
`weekday,start,end,title,mode,location` (Mon..Sun, HH:MM, mode `online` or `in-person`).

## Files
| File | Written by | Content |
|---|---|---|
| `*.ics` | athlete (export) | raw calendar, kept as the source of truth |
| `manual.csv` | athlete or coach | weekly classes typed by hand, optional |
| `overrides.json` | coach | `{"title substring": "online" \| "in-person" \| "ignore"}` when the heuristic gets a class wrong |
| `classes.json` | tool (or coach via connector) | one row per occurrence: `{date, start, end, all_day, title, mode, location, calendar, uid, source}` |

`mode` is `in-person`, `online`, `unknown` (no room, no link: ask) or `all-day` (deadlines, holidays).

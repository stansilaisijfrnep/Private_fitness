# Feed & Load dashboard

Live page: https://claude.ai/code/artifact/b7cdec67-42a2-4075-bd10-a4e797e91546
Works on phone and laptop when signed in to claude.ai. Private to the owner.

`index.html` is the page source (a fragment: the Artifact tool wraps it in doctype, head and body).
Republish it with the Artifact tool, passing the URL above as `url`, whenever the program or
targets change. Never publish without the URL, that creates a second page.

## Views
- **Today**: the scheduled session for the date, rings for calories, protein and sessions this week,
  the coach's latest note, and set-by-set input (load, reps, RIR) that saves to the shared database.
  Sport sessions and rest days are handled by the selector.
- **Week**: Monday to Sunday with done / today / planned / missed. Tap a day to log it.
- **Progress**: 7-day bodyweight average, sessions, protein, sleep; bodyweight chart, strength chart
  (estimated 1RM per session, per lift), calories and protein for 14 days; forms to log bodyweight and
  a day of food.
- **Program**: the current block, targets, rules.

## Database layout (artifact db, read with `read_db`, write with `write_db`)
| Collection / doc | Written by | Content |
|---|---|---|
| `sessions/<YYYY-MM-DD>_<dayKey>` | page | `{type:"lift", date, dayKey, name, week, sleep, bodyweight, energy, duration, notes, exercises:[{k, n, sets:[{load, reps, rir}], note}], savedAt}` |
| `sessions/<YYYY-MM-DD>_sport` | page | `{type:"sport", date, kind, minutes, rpe, note}` |
| `bodyweight/<YYYY-MM-DD>` | page or coach | `{date, weight, waist, source}` |
| `nutrition/<YYYY-MM-DD>` | coach after each meal, or page | `{date, kcal, protein, carbs, fat, note, source}` |
| `settings/targets` | coach | `{kcal, protein, carbs, fat, sleep, sessions}` overrides the page defaults |
| `coach/latest` | coach | `{date, text}` shown at the top of Today |

dayKey is one of `upper, lowerA, push, pull, legsB`. Exercise keys (`k`) are in `index.html` under PROGRAM.

## Coach workflow with the dashboard
1. Start of every session: `read_db` the `sessions`, `bodyweight` and `nutrition` collections
   (query with `date >= last synced date`). Sync anything new into `logs/`, review it, then commit.
2. After estimating a meal in chat: update `nutrition/<date>` with the running daily totals.
3. After a bodyweight reading in chat: set `bodyweight/<date>`.
4. After coaching a session or setting next targets: set `coach/latest` with a one or two sentence note.
5. Calorie or protein change: update `settings/targets` and `profile/PROFILE.md`.
6. Program change: edit PROGRAM in `index.html` and `program/current.md`, republish with the URL.

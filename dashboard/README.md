# Feed & Load dashboard

Live page: https://claude.ai/code/artifact/b7cdec67-42a2-4075-bd10-a4e797e91546
Works on phone and laptop when signed in to claude.ai. Private to the owner.

`index.html` is the page source (a fragment: the Artifact tool wraps it in doctype, head and body).
Republish it with the Artifact tool, passing the URL above as `url`, whenever the program or
targets change. Never publish without the URL, that creates a second page.

## Views
- **Dashboard** (first page): next session with a Start training button, rings for calories, protein
  and sessions this week, today's food numbers with macro bars, 7-day tiles, bodyweight chart, strength
  chart (estimated 1RM per session, per lift), calories and protein for 14 days, forms to log bodyweight
  and a day of food.
- **Calendar**: Outlook-style month grid. Each day shows its session as a chip (today, planned, done,
  skipped, sport). Tap a day to open it. "Coming up" lists the next five sessions.
- **Session**: the day's session as a structured overview (exercise, sets × reps, RIR, target load,
  last time) with a Start training button. Logging mode shows a timer, set counter, sleep / weight /
  energy fields, and a row per set for kg, reps, RIR. Save writes to the shared database. A selector
  changes the session type, and a sport session can be logged on any day.
- **Program**: the current block, targets, rules.

The schedule is a rolling order (Upper, Lower A, Push, Pull, Legs B), five sessions per week on any
day. The page computes the plan from the sessions already logged: the next session in the order is
projected onto the remaining days of the current week, weekdays first, weekend if the weekdays run
out. Past days in a finished week with fewer than five sessions show "Missed" on weekdays. No coach messages are shown on the page
by the athlete's request; coaching happens in chat.

## Database layout (artifact db, read with `read_db`, write with `write_db`)
| Collection / doc | Written by | Content |
|---|---|---|
| `sessions/<YYYY-MM-DD>_<dayKey>` | page | `{type:"lift", date, dayKey, name, week, sleep, bodyweight, energy, duration, notes, exercises:[{k, n, sets:[{load, reps, rir}], note}], savedAt}` |
| `sessions/<YYYY-MM-DD>_sport` | page | `{type:"sport", date, kind, minutes, rpe, note}` |
| `bodyweight/<YYYY-MM-DD>` | page or coach | `{date, weight, waist, source}` |
| `nutrition/<YYYY-MM-DD>` | coach after each meal, or page | `{date, kcal, protein, carbs, fat, note, source}` |
| `settings/targets` | coach | `{kcal, protein, carbs, fat, sleep, sessions}` overrides the page defaults |

dayKey is one of `upper, lowerA, push, pull, legsB`. Exercise keys (`k`) are in `index.html` under PROGRAM.

## Coach workflow with the dashboard
1. Start of every session: `read_db` the `sessions`, `bodyweight` and `nutrition` collections
   (query with `date >= last synced date`). Sync anything new into `logs/`, review it, then commit.
2. After estimating a meal in chat: update `nutrition/<date>` with the running daily totals.
3. After a bodyweight reading in chat: set `bodyweight/<date>`.
4. Calorie or protein change: update `settings/targets` and `profile/PROFILE.md`.
5. Program change: edit PROGRAM in `index.html` and `program/current.md`, republish with the URL.
6. Do not add messages, banners or coach notes to the page. The athlete wants numbers and inputs only.

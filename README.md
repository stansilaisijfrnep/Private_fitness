# Private fitness log

A coaching workspace. Claude is the coach, this repo is the coach's memory.

## How to use it

Just talk. In any Claude Code session on this repo:

- **Meal**: paste a photo or write what you ate ("2 eggs, 100 g oats, banana, 300 ml milk").
  It gets estimated, logged to `logs/nutrition/`, and compared to your daily targets.
- **Workout**: write it out ("Bench 80 kg 3x8, last set 1 RIR; rows 70 kg 3x10 ...").
  It gets logged to `logs/training/`, compared to last time, and you get next session's targets.
- **Bodyweight**: "82.4 kg this morning, waist 84 cm". Goes into `logs/bodyweight.csv`.
- **Weekly check-in**: "check-in" on Sunday. The coach reviews the week and adjusts.

## Layout

```
CLAUDE.md              coaching brief, principles, and how each input is handled
profile/PROFILE.md     who you are: stats, history, injuries, goals, targets
program/current.md     the training block you are on right now
logs/training/         one file per session
logs/nutrition/        one file per day
logs/bodyweight.csv    date, weight, waist
logs/checkins/         weekly reviews and decisions
```

Each log folder has a `_TEMPLATE.md` showing the format.

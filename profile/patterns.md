# Athlete patterns (read every session, update after every session and every day of food)

What the logs actually show, not what the plan assumes. Written 2026-09-08 after 3 training days
and 3 logged days of food. Every line here comes from a log entry, not from a guess.

## Training behaviour

### 1. The first work set is always too light
He treats his first work set as another warm-up, finds the real weight on set 2 or 3, and then has
no energy left for a proper top set.

| Exercise | What happened | What it should have been |
|---|---|---|
| Incline DB press, 7 Sep | 18×12, then 20×9, 22×7 | start at 20, work up to 22 |
| Chest press HS, 7 Sep | 20×12, then 25×9, 25×9 | start at 25 per side |
| Chest press HS, 5 Sep | 10/side warm-up, 25×6, then down to 20 | 20 to 22.5 from set 1 |
| Vertical row Nautilus, 5 Sep | 40×9, 50×10, 60×9, 60×8.5 | start at 55 to 60 |
| Seated DB shoulder press, 5 Sep | 12.5×12, then 15×9, 15×9 | start at 15 |
| Seated leg press, 6 Sep | 60×12, 80×11, then he asked for 90×8 himself | start at 80 |
| Crunch machine, 6 Sep | 23×12, then 36×12 | start at 36 |
| DB lateral raise, 7 Sep | 7×12, 7×12, 7×12 - two days after 10×12, 10×10 on 5 Sep | 10 kg; 3 kg per hand left on the table for a whole session |

**Rule for the coach:** never prescribe a "test" or a light opener for an exercise he has done
before. Give one number: last session's load. Warm-ups are warm-ups and are logged as such.

### 1b. He ramps DOWN when he is tired, and the load he handled is the top set
Pull-ups 5 Sep: +5 kg × 4, then bodyweight × 6 and × 5. Incline press 7 Sep: up to 22, then back
to 20 for the last set. Pec deck 7 Sep: 20, then 15, 15. Pushdown 7 Sep: 25, then 20, 20.
Reading the last set as "the working weight" throws that work away and prescribes less than he can
already lift. Fixed 8 Sep in both `suggest()` (dashboard) and `tools/brief.py`: the working load is
the **heaviest load he handled**, counting any set that came within 2 reps of the range.
**He uses added weight on pull-ups. Never prescribe plain bodyweight pull-ups without checking the
added-load history first.**

### 2. He stops at round numbers, not at failure
Lateral raise 7×12, 7×12, 7×12. Pushdown 25×10, 20×10, 20×10. Pec deck 15×12, 15×12.
Hanging leg raise 12, 12. Three sets identical to the rep is a sign the set ended in the head, not
in the muscle. On 6 Sep he stopped lateral raises at 10, was told the last set goes to failure, and
immediately did 14.

**Rule for the coach:** on the last set of every isolation and machine exercise, name the target as
"until you cannot do another clean rep", never a number. He responds to that instruction.

### 3. He never reports RIR unless asked in the same sentence
Three sessions, zero RIR values volunteered. Asking after the set does not work either.
**Rule for the coach:** put "und wie viele hattest du noch drin?" in the same message as the next
set prescription, every time.

### 4. He substitutes barbells for machines and dumbbells, every time
Barbell bench → Hammer Strength iso-lateral press. Barbell overhead press → seated shoulder press
machine. Cable fly → pec deck. Cable lateral raise → dumbbells (explicitly asked for). Hack squat →
seated leg press. Cable crunch → hanging leg raise, then the crunch machine.
The only barbell work he has kept is the squat and the RDL, both of which he is learning.

**Rule for the coach:** prescribe machines and dumbbells by default on upper body. Put barbells only
where technique or loading demands it (squat, RDL, trap bar).

### 5. He adds work on his own when he feels good
Extra leg press set at 90 kg, the crunch machine after the hanging leg raises, a third dip set.
That is motivation, not a problem, but it lands at the end of the session where it adds fatigue and
no stimulus (dips set 3 = 1 rep).

**Rule for the coach:** when he asks for an extra set, say yes on machines and isolation, no on the
exercise that already failed.

### 5b. Exercise order is worth about 5 kg on his pull-ups
5 Sep, pull-ups fourth after pressing and rowing: +5 kg × 4, then bodyweight.
8 Sep, pull-ups first and fresh: +10 kg × 6, 4.5, 4. Double the added load, more reps.
**Rule for the coach:** the lift that matters most goes first. On Push that is now the shoulder
press (his weak point), on Pull it stays the pull-up.
Applied to Upper on 9 Sep: pull-ups moved from third to second, before the vertical row, so the
+10 kg from Pull day carries over. Check on 10 Sep whether it did.

### 5c. His technique calls are trustworthy
T-bar row 8 Sep: 40×8, then 35 with body English — he noticed it himself, said so, and dropped to
30 kg strict for 12. RDL 6 Sep: dropped 50 → 40 on his own to keep the hinge clean.
**Rule for the coach:** when he says a load was moved with swing, believe him and log the strict
load as the working load. Do not push him back up to the swung number.

### 5d. Arms are stronger than the plan assumed
Hammer curl 17.5 kg per hand × 8 (plan said 10 kg). EZ bar curl 30 kg × 10-12 in two sessions.
Cable row 55 kg on the first day. His pulling and arm strength is well ahead of his pressing
(incline 20-22 kg per hand, Hammer press 25 per side). Chest and shoulders are the lagging side,
which matches his own goal list.

### 5e. He reports partial reps as fractions
"6 and the last one almost, like 3/4", "4/5", "8 1/2", "6.8". Convention: log the clean reps plus
0.5 for a partial (4/5 → 4.5, 8 1/2 → 8.5). A partial never counts as a full rep for progression.

### 5f. He skips isolation back work once the back "feels done"
Straight-arm pulldown dropped on 8 Sep after 10 back sets, by his choice, and he asked to go to
biceps. Reasonable. Rear delts he did do when asked (3 sets reverse pec deck).
**Rule for the coach:** put the rear-delt work before the biceps superset, otherwise it is the
first thing to fall off the end.

### 5g. He trains in the evening on weekdays
Push 7 Sep and Pull 8 Sep both ran roughly 19:30 to 21:00. "I train in the afternoon" means
after 19:00. Pre-training food has to be in by 17:30; the post-training meal lands at 21:30 or
later, which is why the last 500-800 kcal of the day are always the hard ones.

### 5h. The timetable, and what it does to the week (imported 9 Sep)
SKEMA in person at Sophia Antipolis: Mon 13:15-16:30, Wed 16:45-20:00, Thu 08:00-16:30.
EADA online: Mon 15:00-18:00, Wed 15:00-17:00. Tuesday and Friday have no classes.
Consequences, all in `data/timetable.json` and printed by the briefing every day:
- Wednesday has **no evening slot** - he is on campus until 20:00. Train in the morning or not at all.
- Thursday starts at 08:00 on campus: breakfast at 07:00 must be the oats bowl, and the whole day
  is packed food (yfood, Wasa, bananas, Barebells) plus a campus lunch. Train at 17:00.
- Monday afternoon is class; train in the morning, lunch by 12:15, yfood in the bag.
- Tuesday and Friday are the easy days: train midday, all meals at home.
**Weekly template from week 2: Mon AM, Tue midday, Wed AM, Thu 17:00, Fri or Sat, Sun rest.**
This kills the week-1 problem of training at 19:30 and chasing 800 kcal at 21:30.

### 5i. Campus sessions get cut by the clock, from the end of the list
9 Sep: Legs B at the campus gym started at 12:15 with a 15:00 class; adductor and abs fell off.
7 Sep: 13 chest sets and the shoulder press nearly fell off. Same shape: whatever is last, dies.
**Rule for the coach:** on a campus day, start by 10:30 for a morning slot and put the small
knee-health work (adductor, Copenhagen, abs) in the FIRST 10 minutes after the warm-up, not the
last. The big lifts survive a cut; the small ones do not.

### 6. Session length and drift
He trains hard but the session drifts: 13 chest sets on 7 Sep before the shoulder press. The fix is
in the plan now (shoulder press second), not in willpower.

## Favourite and disliked exercises

**Food he does not like:** pavé tournedos / plain tenderloin (9 Sep, ate one of two and stopped - taste). Ground beef with sauce and rumsteak he finishes.

**Enjoys and asked for more of:** landing drills (9 Sep, "did them very nice"), wants knee strength and vertical jump as a secondary goal for basketball. Keep 3×5 landings on every leg day; add low-volume box jumps (2-3×3) from block 2.

**Loves / trains hardest:** pull-ups (his best lift, wide grip bodyweight), dips, the Hammer
Strength chest press, dumbbell lateral raises, leg press.
**Accepts:** machine rows, pec deck, pushdowns, hanging leg raises, crunch machine.
**Avoids or refuses:** calves ("I am happy with them", removed from the program 6 Sep),
cable fly (swapped for the pec deck), barbell bench and barbell overhead press.
**Learning, needs patience:** back squat (heels on 1.25 kg plates for depth), RDL (dropped from
50 to 40 kg on his own to keep technique — good judgement).

## Eating behaviour

### 1. Stomach ceiling is on carbs, not on protein
He could not finish 2 bags of rice ("just impossible") but ate 350 g of ground beef the same
evening. On 5 Sep a tuna-rice batch filled 3 burritos and he managed 4/5 of one. On 7 Sep he left
a third of the beef and a third of the rice.
**Rule for the coach:** never prescribe more than ~1 bag of rice or ~150 g dry pasta in one sitting.
Close the carb gap with bread, bananas, honey, jam, skyr and orange juice, not with a bigger bowl.

### 2. He measures in bowls, and the bowl is 500 ml
Calibrated by the athlete on 8 Sep: the bowl he eats from holds 500 ml of water. Every portion he
reports as "a bowl", "2.5 bowls", "1 1/4 bowls" converts through the table at the top of
`profile/foods.md`. Ask for bowls, not grams — that is the unit he actually uses and it is accurate
enough. Only ask for grams when a package label is in his hand.

### 3. Bread works when rice does not
Half a cereal baguette (60 g carbs) went down after a full plate. Two slices at breakfast every day.
**Bread is the carb tool. Rice is the meal, bread is the filler.**

### 4. Breakfast is the fat problem
Eggs plus whole milk, three days running: fat 116 g (6 Sep), 103 g (7 Sep) against an 80 g target,
while carbs finished 100 to 170 g short every day.
**Rule for the coach:** 3 eggs maximum, milk only in the coffee, carbs on the plate first.

### 5. He asks "why", he does not refuse
On 5 and 6 Sep he asked twice why orange juice was in the plan. That was a question about the
reasoning, not a rejection — he drank two glasses that evening and later a third, and on 8 Sep he
said plainly that he likes orange juice. The coach read it as a refusal and was wrong.
**Rule for the coach:** when he asks why, give the reason in one line and keep the prescription.
Never downgrade a food to "optional" just because he questioned it. Only treat something as refused
when he says so (calves: "I am happy with them" — that is a refusal).
Orange juice is a liked food and a useful one: liquid carbs that cost no stomach space, which is
exactly his bottleneck.

### 6. What is actually in the house
Rice, pasta, sauces, eggs, skyr, blueberries, beef, sardines, tuna, mozzarella, bread, bananas.
**Missing since intake: oats, whey, peanut butter, chicken.** The 950 kcal shake from PROFILE rule 3
cannot be made. Either he buys the three items or the plan stops relying on it.

### 7. Protein bars: he buys both good and bad ones
Barebells shake 164 kcal / 24 g protein — good. Nutramino wafer 205 kcal / 7.8 g protein — a
chocolate bar with a label.
**Rule for the coach:** tell him the protein per 100 kcal, not just the macros.

### 8. Where the day is won or lost
Calories and protein land close to target almost every day (3,136 / 199, 3,269 / 164, ~3,125 / 175).
Carbs are short every single day. The shortfall is always in the evening, when he is full.
**Rule for the coach:** front-load carbs. Breakfast and lunch have to carry 250 g of the 475 g.

### 9. The day that worked (8 Sep) - copy it
3 eggs + banana with honey (breakfast) → 1 1/4 bowls mashed potato (lunch) → the skyr bowl with
peanut butter, honey, blueberries and juice (15:30) → baguette, leftovers and juice (19:00) →
training. By 19:00: 2,500 kcal, 114 g protein, **342 g carbs, 71 g fat**. First day with fat under
target and carbs above 300 before the evening. The difference to the three days before: no big
egg-and-milk breakfast, potatoes instead of a second rice bag, the skyr bowl as a real meal, juice
with two meals.

### 9b. The fat leak has moved from eggs to peanut butter
8 Sep: 2 tbsp at 15:30, then 4 tbsp in the evening bowl - 6 tablespoons, about 600 kcal and 46 g
of fat, and the day finished 24 g over on fat despite a clean breakfast. Peanut butter is the food
he over-pours when the spoon is in his hand.
**Rule for the coach:** state "2 tablespoons" every time the bowl is prescribed, and say that the
third spoon of honey is free but the third spoon of peanut butter is not. Skyr itself is unlimited:
a full kilo in a day is 600 kcal and 100 g protein, no problem at all.

### 10. He shops through Uber Eats (Carrefour), and he does buy what is asked for
8 Sep: peanut butter, skyr 1 kg, juice ×2, bread ×3, milk ×3, eggs 15 arrived; oats ×2 and yfood ×8
ordered for the next day. Whey is the only item asked for three times and still not bought.
**Rule for the coach:** give the shopping list as concrete Carrefour items and quantities, one
message, and it gets ordered. Vague "buy more protein" does not.

## The left hamstring (ACL graft site) - his own rule, stated 9 Sep
The ACL graft came out of the left hamstring. It sometimes feels strange under load. He was explicit:
"that does not mean I should train it lightly - I should use heavy weights, but I have to get back
into it first." So: hamstrings get trained hard, ramped over weeks, not avoided. Leg curls and
Nordics are the right tools - the graft tendon regrows only partly and the eccentric strength is
what protects the knee. Ask "left and right the same?" on every hamstring exercise, and log any
asymmetry.

## Coach's own error to never repeat: time of day
9 Sep, 21:40 local: the coach was still prescribing a "14:45 oats bowl" because it inferred the
time from the conversation instead of reading the clock. The container runs on UTC; he lives on
Paris time. `TZ=Europe/Paris date` first, then advice. The briefing prints local time at the top
from now on.

## Sleep
8 Sep: 9 hours (first reported value). Intake said 6 to 7 hours, so this is a real improvement.
Ask for it every morning, log it with the session. Pull session 1 ran on 9 h sleep and 264 g of
carbs and produced the best pull-up set so far - that is not a coincidence, say so when it repeats.

## Recovery
9 Sep 23:20, after five sessions in five days including his first two leg sessions ever: "extremely
sore, whole body". Expected in week 1 (repeated bout effect makes week 2 far milder), but five days
straight on 2200-2700 kcal is the real cause, and the block rule of one rest day in seven had not
been applied. Rest day given for Thu 10 Sep, Upper moved to Fri midday.
**Rule for the coach:** the rolling order does not mean six days in a row. Place the rest day before
the athlete has to ask for it, and put it on the day with the worst logistics (Thursday, campus
08:00-16:30). Soreness alone never cancels an upper session; six days straight plus underfeeding does.

### Recovery: the rest day is his, not a concession
10 Sep was the first rest day of the block, placed by the coach after five days straight.
His verdict: "sehr wichtig ... jetzt wieder superfrisch, superready". He trains hard enough that
the limiter is recovery, not willingness.
**Rule for the coach:** plan five sessions and two rest days into every week, and put a rest day
on the worst logistics day (Thursday, campus 08:00-16:30). Never six days in a row.

## Two gyms, two sets of numbers (rule added 11 Sep)
Fitness Park is the default. The SKEMA campus gym has its own machines and its own stacks: the
Kinesis "level 15" is not 15 kg, the Technogym leg press is not the Nautilus. On 9 Sep the campus
cable RDL was logged under the same key as the barbell RDL and the system then wanted to prescribe
15 kg for a man who pulls 50. Every session now carries `gym` (`fitnesspark` or `campus`), and both
the briefing and the dashboard prescribe only from the same gym.

## Coaching mode (his decision, 11 Sep)
He wants a training coach. Nutrition coaching only when he asks, uploads something, reports a meal
or sends a weight reading - then full professional, then back to training. Logging never stops.

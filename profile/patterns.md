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

### 6. Session length and drift
He trains hard but the session drifts: 13 chest sets on 7 Sep before the shoulder press. The fix is
in the plan now (shoulder press second), not in willpower.

## Favourite and disliked exercises

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

## Sleep
8 Sep: 9 hours (first reported value). Intake said 6 to 7 hours, so this is a real improvement.
Ask for it every morning, log it with the session.

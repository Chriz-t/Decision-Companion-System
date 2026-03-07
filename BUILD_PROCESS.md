# BUILD_PROCESS.md

## LaptopIQ — Decision Companion System

---

## How I Started

The assignment asked for a system that helps a user make better decisions by accepting multiple options,
evaluating them against weighted criteria, and explaining the recommendation. My first instinct was to
reach for a well-known academic framework for exactly this kind of problem: Multi-Criteria Decision
Analysis (MCDA).

The specific approach I initially chose was a **Weighted Sum Model (WSM)** combined with
**Analytic Hierarchy Process (AHP)** for weight extraction, delivered as a **command-line tool**.

The reasoning at the time:

- WSM is the most widely taught MCDA method — straightforward to implement and explain
- AHP is the standard academic technique for deriving weights from user preferences through
  pairwise comparisons, which felt rigorous
- A CLI felt appropriate for a first prototype — no frontend overhead, fast to build

---

## The First Implementation — WSM + AHP (CLI)

### How it worked

The CLI asked the user to compare every pair of criteria (price vs RAM, price vs CPU, RAM vs CPU,
and so on) on a scale of 1–9, following the standard Saaty AHP scale. From these comparisons a
pairwise matrix was constructed, its principal eigenvector was extracted, and the resulting vector
became the weights. Each laptop was then scored as:

```
WSM Score = w_price * norm_price + w_ram * norm_ram + w_cpu * norm_cpu + ...
```

All features were normalised to [0,1] with MinMaxScaler before scoring. Laptops were ranked by
score descending — highest score wins.

### What seemed to work

- The math was sound and well-documented in literature
- Weight derivation felt principled — eigenvector extraction from a pairwise matrix has a
  theoretical basis in preference consistency
- The Consistency Ratio (CR) check from AHP flagged when the user's comparisons were
  logically contradictory

---

## Problems I Found — Why I Moved Away

### Problem 1: WSM Compensation

This was the most damaging flaw for this specific use case.

WSM allows a very high score on one criterion to **compensate** for a poor score on another. In
practice, this meant a laptop with an excellent CPU and GPU but a price well above the user's budget
could outscore a laptop that was within budget with decent specs — because the performance gains
numerically cancelled out the price penalty.

For laptop buying, this is the wrong behaviour. A user who sets a budget of ₹80,000 is not saying
"I would like to spend ₹80,000 ideally but a ₹1,40,000 laptop is fine if the CPU is fast enough."
They are setting a constraint. WSM treated every criterion as a dial on the same scale and let them
trade off freely, which produced recommendations that consistently favoured the most powerful and
expensive laptops regardless of how the weights were set.

Changing the weights only slightly — say, reducing CPU weight from 30 to 20 — barely shifted the
rankings because the top laptops dominated across most dimensions simultaneously. The model was
not sensitive to the user's priorities in the way that matters.

### Problem 2: AHP Pairwise Comparison was Cumbersome

AHP requires the user to make **n(n-1)/2** pairwise comparisons. With 5 criteria (price, RAM, CPU,
GPU, storage) that is 10 questions, each requiring a judgment like:

```
How much more important is RAM than storage?
  1 = equal, 3 = moderate, 5 = strong, 7 = very strong, 9 = extreme
```

In testing this with the laptop dataset, users found this process confusing and counterintuitive.
The scale of 1–9 has no natural meaning to someone deciding on a laptop. "Is RAM 3x or 5x more
important than storage?" is not a question most people can answer with confidence.

More practically, the pairwise matrix needs to be **consistent** — if you say price is 3x more
important than RAM and RAM is 3x more important than GPU, you must say price is roughly 9x more
important than GPU, otherwise the CR check fails and the weights are unreliable. Users frequently
triggered inconsistency warnings and had no intuitive way to correct their answers.

### Problem 3: CLI Was Not User-Friendly

Beyond the AHP usability issue, a CLI is a poor interface for a decision tool that a non-technical
user should be able to use. There was no visual feedback on how weights compared to each other,
no way to quickly try different scenarios, and results were printed as a plain table with no
context about why each laptop ranked where it did.

---

## How My Thinking Evolved

The core insight from the WSM failure was that laptop buying involves **goals with directions**,
not just preferences. The user is not trying to maximise a single composite score. They are trying
to find a laptop that meets a set of requirements, and the question is which laptop comes closest
to meeting all of them simultaneously.

This framing pointed directly to **Goal Programming**, a technique from Operations Research designed
exactly for this situation. Instead of scoring laptops by how good they are in absolute terms, Goal
Programming scores them by how much they **deviate from the user's stated goals** — and only
penalises deviations in the direction that matters.

For price, deviation is penalised only when the laptop costs more than the goal (over budget is bad;
under budget is fine). For RAM, deviation is penalised only when the laptop has less than the goal
(falling short is bad; exceeding is fine). This asymmetric, directional evaluation reflects how
people actually think about purchase constraints.

The WSM compensation problem disappears because a laptop does not get "credit" for having a great
GPU that offsets an overpriced tag. Each criterion is evaluated independently and only in the
relevant direction.

### Weight Input Redesign

Instead of AHP pairwise comparison, I replaced weight input with **simple sliders** — one per
criterion, ranging 0 to 100. The values are normalised to proportions before use, so only the
ratios matter. A user who sets price=50 and RAM=25 is saying price is twice as important as RAM.
This is immediately understandable without any instruction.

The total of all sliders is displayed in real time. While it does not need to equal 100 (the
normalisation handles any total), the badge turning green at exactly 100 gives users a satisfying
confirmation that their priorities are fully distributed — which in practice guides them toward
more deliberate choices.

### Moving to a Flask Web App

Once the model changed to Goal Programming, it became natural to also fix the interface. Flask
was chosen because it is minimal — no boilerplate, no configuration, just routes and templates.
The entire frontend is a single HTML file with inline CSS and vanilla JS, so the project has no
build step and can be run with a single `python app.py` command.

The web interface made it easy to add two things that the CLI could not:

- **Real-time slider feedback** — users see their priorities updating as they drag
- **Per-card explanations** — each result card shows a breakdown of which goals were met and
  which were missed, with the magnitude of any shortfall

---

## Alternative Approaches Considered

### TOPSIS

TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) ranks options by their
geometric distance from an ideal best point and an ideal worst point. It is more sophisticated
than WSM and partially addresses the compensation problem by using Euclidean distance rather than
linear summation. I considered it after finding WSM's flaws.

I rejected it for two reasons. First, it still lacks directional asymmetry — a laptop that
exceeds your RAM goal gets "credit" that can offset a price overrun, which is the same compensation
issue in a different form. Second, the ideal best and worst points are derived from the dataset
itself, which means the ranking changes if the dataset changes, making it harder to explain to a
user why a specific laptop was recommended.

### Storing Weights Across Sessions

I considered persisting user preferences in a database or session cookie so returning users would
not need to re-enter their goals. I deferred this because it adds infrastructure (SQLite or a
session layer) without improving the core decision logic. The current in-memory approach is simpler
and the form defaults are set to sensible values (₹80,000 budget, 16 GB RAM, etc.) that provide
a working starting point.

### AI-Generated Rankings

The assignment permitted AI use. I considered using a language model to rank laptops directly
from a natural language description of needs. I rejected this as the primary ranking mechanism
because the output would not be reproducible or auditable — the same inputs could produce
different orderings across runs, and there would be no formula to point to when explaining why
laptop A outranked laptop B. AI is used only in the explanation text generation, where variability
is acceptable and the underlying decision (the rank) is already fixed by the mathematical model.

---

## Refactoring Decisions

### CPU Score Engineering

The raw dataset has processor brand, name, and generation as strings — there is no numeric
performance column. The first version of preprocessing simply dropped the CPU column, which meant
the model could not distinguish between an i3 and an i9.

I introduced a hand-crafted `compute_cpu_score()` function that assigns points for brand tier
(i3=3, i5=5, i7=7, i9=9, Ryzen equivalents, Apple M-series) and adds a generation multiplier.
This is a heuristic — it is not calibrated to real benchmark data — but it is transparent,
adjustable, and orders processors in a directionally correct way.

### Scaling Strategy

Early versions of the model applied `MinMaxScaler` inside the `GoalProgramming` class on every
request. This was moved to `DataPreprocessor.preprocess()` at startup so that scaling is done once
and the scaled columns are stored in the DataFrame. The `GoalProgramming` class operates on the
original (unscaled) values for deviation calculation, which keeps the deviation formula readable
and grounded in the user's actual units (₹, GB, etc.) rather than abstract scaled values.

### Explanation as a Separate Method

Initially the explanation strings were assembled in `app.py` alongside the response formatting
logic. This was refactored into a dedicated `GoalProgramming.explain()` method so that the
explanation logic lives next to the deviation logic it describes. A change to the deviation formula
now only requires a corresponding change in one place.

---

## Mistakes and Corrections

**Mistake:** The first WSM implementation scored price directly (higher price = higher score when
normalised), which meant expensive laptops scored better on the price criterion. The fix was to
invert the price scale: `price_scaled = 1 - price_scaled` so that a lower price yields a higher
score.

**Mistake:** AHP weight extraction was implemented correctly but the CR threshold of 0.1 was too
strict for 5 criteria. Almost every test run triggered the inconsistency warning and asked the user
to redo comparisons. Relaxing to 0.15 helped but did not solve the underlying usability problem,
which led to dropping AHP entirely.

**Mistake:** The initial Goal Programming implementation penalised price deviation symmetrically —
both over-budget and under-budget were penalised. This was wrong conceptually (finding a ₹50,000
laptop when your goal is ₹80,000 is not a problem) and was corrected to one-directional penalties.

**Mistake:** `ssd_gb` and `hdd_gb` were dropped before the API response was assembled, so the
frontend could not distinguish between SSD-only, HDD-only, and hybrid storage configurations.
The fix was to pass both columns through to the response and build the storage label
(`512 GB SSD + 1024 GB HDD`) in the frontend using a `storageLabel()` helper function.

---

## What Changed During Development and Why

| Stage | Approach | Reason for Change |
|---|---|---|
| v1 | WSM + AHP, CLI | Initial prototype based on academic MCDA methods |
| v2 | Goal Programming, CLI | WSM compensation and AHP usability problems |
| v3 | Goal Programming, Flask web app | CLI too friction-heavy; web enables slider UI and visual results |
| v4 | Added `explain()` method | Results without reasoning did not satisfy the "explainability" requirement |
| v5 | Storage type, display, warranty label fixes | Cards displayed raw numbers without context (e.g. "512" instead of "512 GB SSD") |
| v6 | Input validation (min/max bounds) | Users could enter physically impossible values (e.g. CPU score of 999) |

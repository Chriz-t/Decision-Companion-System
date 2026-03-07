# RESEARCH_LOG.md

## LaptopIQ — Decision Companion System

> This log documents every query, reference, and AI interaction made during the development of this
> project. For each AI prompt, it records what was asked, what was accepted, what was rejected or
> modified, and why. Sources that influenced architectural or algorithmic decisions are noted
> separately.

---

## Legend

| Tag | Meaning |
|---|---|
| `[AI]` | Prompt sent to an AI assistant |
| `[SEARCH]` | Web / documentation search |
| `[READ]` | Article, paper, or documentation page studied |

---

## Phase 1 — Problem Exploration

---

### `[AI]` What are some good examples of a decision companion system?

**What the AI returned:**
A list of examples including travel planners (comparing destinations by cost, climate, safety),
job candidate screeners (ranking applicants by skill match), financial portfolio advisors
(balancing risk and return), laptop and product recommenders, and diet/meal planners. It also
mentioned commercial products like IBM Watson Decision Platform and various MCDA-based tools used
in urban planning and healthcare.

**What I accepted:**
The framing that a decision companion system is fundamentally about helping a user navigate a
**multi-criteria trade-off** — not just searching a database. This influenced the decision to
use a structured mathematical model rather than keyword filtering.

**What I rejected:**
Commercial enterprise examples (Watson, SAP analytics) — too complex and out of scope for a
take-home assignment. Also rejected the idea of using a recommendation engine with collaborative
filtering (e.g. "users like you chose X") because it requires historical user data that does not
exist in this context.

---

### `[AI]` Are there any related topics I should research?

**What the AI returned:**
Suggested researching: Multi-Criteria Decision Analysis (MCDA), Decision Support Systems (DSS),
Analytic Hierarchy Process (AHP), TOPSIS, Goal Programming, Weighted Sum Model (WSM),
Weighted Product Model (WPM), and ELECTRE. Also pointed to Operations Research as the parent
discipline.

**What I accepted:**
Used this as a reading list. Prioritised MCDA, AHP, WSM, and Goal Programming as the most
relevant and accessible methods.

**What I rejected:**
ELECTRE and WPM — ELECTRE involves outranking relations that are difficult to explain to a
non-technical user, and WPM is mathematically equivalent to WSM in log space with no meaningful
benefit for this use case.

---

### `[SEARCH]` Decision Support System

**Source:** Wikipedia — Decision Support System  
**Key takeaway:** A DSS is distinguished from a simple reporting tool by its ability to
model "what-if" scenarios. The ability to change inputs and get different outputs is a core
requirement — not a nice-to-have. This reinforced the design decision to make goals and weights
fully adjustable by the user.

---

### `[SEARCH]` Multi-Criteria Decision Analysis

**Source:** Wikipedia — Multiple-criteria decision analysis; Belton & Stewart (2002) overview  
**Key takeaway:** MCDA methods are divided into value-based methods (WSM, TOPSIS), outranking
methods (ELECTRE, PROMETHEE), and goal/target-based methods (Goal Programming). The choice of
method determines what "best" means — highest composite score vs. closest to stated goals vs.
best relative to others on each criterion independently.

**Influence on project:** Understanding this taxonomy was the foundation for the eventual switch
from WSM (value-based) to Goal Programming (target-based) after encountering the dominance bias
problem.

---

### `[SEARCH]` Weighted Sum Model

**Source:** Decision-making lecture notes (ResearchGate); Triantaphyllou (2000)  
**Key takeaway:** WSM is the simplest MCDA method. Score = sum of (weight × normalised value).
Its main known weakness is **full compensability** — a very high value on one attribute can
offset a low value on another. The literature explicitly flags this as a problem when criteria
have hard constraints rather than soft preferences.

**Influence on project:** This warning was noted but I proceeded with WSM for the first prototype
anyway, intending to test whether compensability was actually a problem in the laptop context.
It was.

---

### `[AI]` I want a laptop decision companion system implementing MCDM. If the weights are the same, how will different users get different results?

**What the AI returned:**
Explained that if weights are identical, the only way two users get different results is if their
**goal values differ** (one user's budget is ₹60,000, another's is ₹1,20,000). With WSM and
identical normalisation, identical weights and identical goals produce identical rankings for all
users. The AI suggested that goal-setting (target values) is what personalises a recommendation,
not just weighting.

**What I accepted:**
This was an important insight. It confirmed that the system must collect both goal targets (what
the user wants) and weights (how much each goal matters), not just one of the two. A pure
weighting system without targets cannot personalise.

**What I rejected:**
The AI suggested adding user profiles / preference history as a third personalisation axis.
Rejected as out of scope.

---

## Phase 2 — Method Selection

---

### `[AI]` Explain the different methods for extracting user weightage

**What the AI returned:**
Covered five methods:
1. **Direct rating** — user assigns a score (0–100) to each criterion
2. **Point allocation** — user distributes a fixed budget of points (e.g. 100) across criteria
3. **Pairwise comparison (AHP)** — user compares every pair of criteria on a 1–9 scale
4. **Swing weighting** — user ranks criteria and estimates how much moving each from worst to best
   "swings" the overall outcome
5. **Trade-off analysis** — user is shown pairs of options and chooses preferred one; weights are
   inferred statistically

**What I accepted:**
Used AHP for the first implementation (seemed academically rigorous), then moved to point
allocation via sliders for the final implementation (more intuitive, less cognitive load).

**What I rejected:**
Swing weighting and trade-off analysis — both require the user to reason about hypothetical
options rather than their actual preferences directly, which adds friction without clear benefit
for a self-service web tool.

---

### `[SEARCH]` Pairwise Comparison — Analytic Hierarchy Process (AHP)

**Source:** Saaty, T.L. (1980) *The Analytic Hierarchy Process*; GeeksforGeeks AHP tutorial  
**Key takeaway:** AHP derives weights from a pairwise comparison matrix. The principal eigenvector
of the matrix gives the weights. A Consistency Ratio (CR) below 0.1 indicates acceptable
consistency in the user's judgments. For n=5 criteria, 10 pairwise comparisons are required.

**Influence on project:** Implemented this fully in the first CLI prototype. The consistency check
was useful in theory but in practice users found the scale confusing and frequently produced
inconsistent matrices.

---

### `[SEARCH]` Trade-off Analysis — Swing Weighting

**Source:** Goodwin & Wright (2004) *Decision Analysis for Management Judgment*  
**Key takeaway:** Swing weighting asks the user to imagine each criterion swinging from its worst
to best value and rate the relative impact. Produces more stable weights than direct rating because
it anchors the comparison in the actual range of the data.

**Influence on project:** Considered as a replacement for AHP after AHP proved cumbersome. Rejected
because implementing it properly requires knowing the min/max range of each attribute in the
dataset first, which would have required tighter coupling between the UI and the data layer.
Sliders were simpler and good enough.

---

## Phase 3 — First Implementation (WSM + AHP + CLI)

---

### `[AI]` How do I structure my code for this project and the overall architecture?

**What the AI returned:**
Recommended separating the project into three modules: data preprocessing, weight extraction,
and the MCDA scoring/ranking engine. Suggested a main entry point that orchestrates all three.
For the CLI version, recommended using Python's `input()` for the AHP comparison prompts and
`pandas` for the data layer.

**What I accepted:**
The three-module separation: `data_preprocessing.py`, a weight extraction module (AHP), and a
scoring module (initially WSM, later Goal Programming). This structure was kept through all
subsequent refactoring.

**What I rejected:**
The suggestion to use `argparse` for CLI arguments. Since the AHP interaction is inherently
interactive (multiple rounds of questions), a flag-based CLI made no sense. Used plain `input()`
prompts instead.

---

### `[AI]` How should the data be normalised?

**What the AI returned:**
Explained Min-Max normalisation and Z-score normalisation. Recommended Min-Max for MCDA because
it scales all values to [0,1] without assuming a normal distribution, which is appropriate for
heterogeneous attributes like price (₹), RAM (GB), and display size (inches).

Also noted that **price should be inverted** after scaling (`price_scaled = 1 - price_scaled`)
because lower price is better, while the raw normalisation would give higher scores to more
expensive laptops.

**What I accepted:**
Min-Max scaling via `sklearn.preprocessing.MinMaxScaler`. The price inversion insight was
directly implemented and caught a bug in the first version that was causing expensive laptops to
score highest on the price dimension.

**What I rejected:**
Z-score normalisation — requires the data to be approximately normal, which commodity prices and
RAM sizes are not.

---

### `[AI]` The dataset has brand name, processor model, and generation as strings. How do I convert this into a comparable numeric criterion?

**What the AI returned:**
Suggested three approaches:
1. Look up a benchmark database (Cinebench, Passmark) and join on processor name
2. Create an ordinal mapping (i3=1, i5=2, i7=3, i9=4) and multiply by generation
3. Build a composite scoring function that combines brand tier, processor tier, and generation
   number using weighted addition

**What I accepted:**
Approach 3 — a composite `cpu_score()` function. Approach 1 would require an external API or
a maintained lookup table. Approach 2 was too coarse (it ignores generation entirely).

**What I modified:**
The AI's initial composite formula treated all brands on the same scale without acknowledging
that AMD Ryzen series numbers (3000, 5000, 7000) are not generation numbers in the Intel sense.
The generation multiplier was adjusted separately for Intel (`gen * 0.5`), AMD
(`(series // 1000) * 1.5`), and Apple (handled in tier score since M1/M2/M3 encode both tier
and generation).

---

### `[AI]` There are processors other than Intel i-series — Ryzen and Apple M-series. How do I calibrate scores across these?

**What the AI returned:**
Proposed a brand-weight multiplier (Intel=1.0, AMD=1.0, Apple=1.2 for efficiency advantages)
combined with tier mapping per brand and a generation bonus. Gave starting values for each
mapping.

**What I accepted:**
The structure of brand weight × tier score × generation bonus. Apple receiving a slight brand
multiplier (1.2) to reflect the MacBook's efficiency-per-watt advantages that raw clock-speed
tier comparisons miss.

**What I modified:**
The AI's Ryzen generation score used the raw series number directly (e.g. 7000 × 0.001 = 7).
Changed to integer division (`7000 // 1000 = 7`) multiplied by 1.5 so the generation contribution
is on a comparable scale to Intel's generation score.

---

### `[SEARCH]` Relevant attributes for laptop recommendation

**Source:** Various laptop buying guides (NotebookCheck, Tom's Hardware, Wirecutter)  
**Key takeaway:** The most universally relevant attributes for a general-purpose laptop
recommendation are: price, RAM, CPU, GPU (for graphics-dependent tasks), storage (type and
capacity), display size, battery life, and weight. Warranty and ratings are secondary quality
signals.

**Influence on project:** Narrowed the active criteria to price, RAM, CPU score, GPU, and storage
as the five goal-setting dimensions. Display size and warranty are shown on the result cards
but not used as goal criteria because they are more of a "nice to have" filter than a
performance constraint for most users.

---

### `[AI]` Let's start on the data preprocessing module with CPU score in mind

**What the AI returned:**
Generated a full `DataPreprocessor` class with `load_data()`, `extract_number()`,
`convert_storage_to_gb()`, `encode_weight_type()`, `compute_cpu_score()`, and `preprocess()`
methods. Used regex for value extraction and `MinMaxScaler` for normalisation.

**What I accepted:**
The overall class structure and the regex-based `extract_number()` and `convert_storage_to_gb()`
helpers. These handled edge cases (TB vs GB, missing values returning 0) cleanly.

**What I modified:**
The `compute_cpu_score()` function required significant manual calibration — particularly the
AMD generation handling and the Apple M-series tier assignments. The AI's initial version
returned unrealistically high scores for older AMD processors because it misread the 4-digit
series number as a generation multiplier directly.

---

### `[AI]` Write the code for an AHP module to extract weights from the user for a set of attributes

**What the AI returned:**
A complete AHP implementation with pairwise comparison input loop, matrix construction,
eigenvector extraction using `numpy.linalg.eig`, weight normalisation, and Consistency Ratio
calculation using the Random Index table.

**What I accepted:**
The matrix construction and eigenvector extraction logic. The mathematical implementation was
correct and matched the Saaty reference.

**What I rejected:**
The input loop formatting — the AI generated prompts like `"Enter value for (price vs ram): "`
with no guidance on what the scale means. Replaced with prompts that included the 1–9 scale
definition and an example.

---

### `[AI]` Explain the consistency check in AHP

**What the AI returned:**
Explained that the Consistency Index (CI) = (λ_max - n) / (n - 1), where λ_max is the principal
eigenvalue and n is the number of criteria. The Consistency Ratio (CR) = CI / RI, where RI is
the Random Index for a matrix of size n (tabulated values from Saaty). A CR below 0.1 is
considered acceptable.

**What I accepted:**
The formula and the RI table values. Implemented the CR check exactly as described.

**What I modified:**
The threshold. The AI used 0.1 strictly. After testing, this was too strict for 5-criterion
comparisons — almost all real user inputs triggered the warning. Relaxed to 0.15. Eventually
the entire AHP module was replaced and this became moot.

---

### `[AI]` Write the code for the MCDA module implementing Weighted Sum Model

**What the AI returned:**
A `WeightedSumModel` class with a `score()` method that multiplied each normalised attribute
by its corresponding weight and summed them, and a `rank()` method that sorted the DataFrame
by score descending.

**What I accepted:**
The class structure and the scoring logic. Mathematically straightforward and correct.

**What I rejected:**
Nothing in this implementation was wrong — the problem was with the model itself, not the
code.

---

## Phase 4 — Discovering the Dominance Bias Problem

---

### `[AI]` The MCDA model keeps giving the most expensive, best-performing laptop as the top result. Only minor changes happen when weights are adjusted. Why does this happen?

**What the AI returned:**
Identified this as the **compensation effect** (also called dominance bias) in WSM. When one
option scores highly across all criteria, changes in weights shift its score proportionally but
rarely change which option leads — because the dominant option still scores well even after
reweighting. The AI named this as a known limitation of additive value models and pointed to
Goal Programming and TOPSIS as methods that reduce or eliminate it.

**What I accepted:**
The diagnosis. The explanation of why the top laptop dominated — it scored high on CPU, GPU, and
RAM while only losing on price, but the weighted sum of its advantages exceeded the price penalty
at almost any reasonable weight combination.

The suggestion to look at Goal Programming specifically.

**What I rejected:**
The suggestion to fix WSM by adding penalty terms for budget violations inline. This would
have been a patch that turned WSM into an ad-hoc version of Goal Programming with less
theoretical grounding. Better to use the right tool.

---

### `[SEARCH]` Point Allocation as a weight elicitation method

**Source:** von Winterfeldt & Edwards (1986); MCDA course notes  
**Key takeaway:** Point allocation (distributing 100 points across criteria) produces weights
that are directly interpretable as percentages of total importance. Cognitively lighter than
AHP, produces similar weight accuracy for most practical decisions.

**Influence on project:** Replaced AHP sliders with point-allocation-style sliders in the final
web UI. The "Total: 100 pts" badge was added to guide users toward a meaningful distribution.

---

### `[SEARCH]` Goal Programming

**Source:** Charnes & Cooper (1961) original paper summary; Wikipedia — Goal Programming;
Tamiz, Jones & Romero (1998) review  
**Key takeaway:** Goal Programming minimises the sum of weighted deviations from target values.
Crucially, it uses **one-sided deviations** — you only penalise deviations in the direction that
matters (over-budget for cost, under-target for benefits). This eliminates the compensation
effect because exceeding a goal provides no reward that could offset failing another goal.

**Influence on project:** Directly replaced WSM. The deviation formula became the core of
`GoalProgramming.compute_deviation()`.

---

### `[AI]` Can Goal Programming resolve the dominance bias shown by WSM?

**What the AI returned:**
Confirmed that Goal Programming resolves the compensation/dominance issue by design. Since
exceeding a goal (e.g. having more GPU than required) gives zero benefit in the score, a
top-end laptop does not accumulate "excess credit" that offsets its high price. Only failures
to meet goals are penalised.

Also noted a practical implication: if the user sets ambitious goals that no laptop can meet,
all laptops will have non-zero deviation scores — which is informative (it tells the user their
expectations may need adjusting) rather than misleading (WSM would still return a confident
top-1 recommendation).

**What I accepted:**
Everything. This confirmed the switch to Goal Programming was the right architectural decision.

---

## Phase 5 — Goal Programming Implementation

---

### `[AI]` Let's try the Goal Programming approach (implementation)

**What the AI returned:**
Generated a `GoalProgramming` class with `__init__(goals, weights)`, `compute_deviation(row)`,
and `rank_laptops(df)` methods. The deviation function checked direction per criterion and
applied weighted partial deviations.

**What I accepted:**
The overall structure and the one-sided deviation logic.

**What I modified:**
The initial version penalised price deviation symmetrically (both over- and under-budget).
Corrected to only penalise `actual > goal` for price. Also added normalisation of deviations
by the goal value (`deviation / goal`) so that a ₹10,000 price overrun and a 2 GB RAM shortfall
are expressed on a comparable scale regardless of their different units.

---

## Phase 6 — Web App and UI

---

### `[AI]` Create a Flask web app based on the laptop recommendation CLI code

**What the AI returned:**
Generated a Flask `app.py` with `GET /` and `POST /recommend` routes, a Jinja2 template
(`index.html`) with a form for goals and sliders for weights, and a JavaScript `renderResults()`
function to display the result cards dynamically.

**What I accepted:**
The overall Flask structure, the route design, and the JavaScript fetch/render pattern. The
generated code was clean and required minimal restructuring.

**What I modified:**
The weight normalisation was initially done in the frontend (dividing each slider value by the
sum). Moved to the backend (`app.py`) so that the normalisation logic is in Python and the
frontend just passes raw slider values. This makes the backend testable independently of the UI.

The result card layout was redesigned — the generated template used a plain `<ul>` list. Replaced
with styled cards with rank numbers, spec pills, and a price tag.

---

### `[AI]` Add an explanation for the recommendation, fix storage display to show SSD/HDD/both, show warranty as "X year warranty", and display as "X inch display"

**What the AI returned:**
Suggested adding an explanation section to each card, passing `ssd_gb` and `hdd_gb` separately
in the API response, and using template literals in JavaScript to construct the label strings.

**What I accepted:**
The approach of passing both storage columns through the API and building the label client-side.
The `storageLabel()` and `warrantyLabel()` helper functions in JavaScript.

**What I modified:**
The explanation generation was moved into a dedicated `GoalProgramming.explain()` method in
Python (server-side) rather than constructing it in JavaScript (client-side). This keeps the
explanation logic next to the deviation logic it describes, and means the reasoning is generated
by the same code that produced the score — not reconstructed independently on the frontend.

---

## Summary: What I Accepted, Rejected, and Modified from AI Outputs

| Area | Accepted | Rejected | Modified |
|---|---|---|---|
| Architecture | Three-module separation | Argparse CLI, collaborative filtering | — |
| Normalisation | MinMaxScaler, price inversion | Z-score | — |
| CPU Score | Composite function structure | Raw ordinal mapping, external API | AMD generation multiplier, Apple M calibration |
| AHP | Matrix math, eigenvector extraction | Input prompt formatting | CR threshold (0.1 → 0.15, then dropped) |
| WSM | Class structure, scoring formula | — | — (model itself replaced) |
| Goal Programming | One-sided deviation structure | Symmetric price penalty | Deviation normalised by goal value |
| Flask app | Route design, fetch/render pattern | Plain list UI | Weight normalisation moved server-side |
| Explanations | `explain()` method concept | Client-side explanation reconstruction | Moved to GoalProgramming class |
| Storage display | Separate ssd_gb/hdd_gb fields | — | Helper functions written manually |
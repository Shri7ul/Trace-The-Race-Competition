# Trace the Ace — Phase 2 Advanced EDA & Architecture Diagnostics
## Final Robust 3-Notebook Implementation Plan

> **Status:** Phase 1 Data Foundation is frozen and certified.  
> **Purpose:** Phase 2 will not re-check data quality, re-parse transcripts, inspect rows manually, or train the production retrieval/model stack. Its job is to discover and rigorously validate the **dialogue, temporal, objective-conditioned, pairwise, and multivariate relationships** that should drive Phase 3 retrieval and the later mastery model.

---

# 0. Why This Phase Exists

Trace the Ace is not a normal tabular classification problem.

The prediction unit is:

$$
\boxed{
\text{Session} \times \text{Learning Objective}
\rightarrow
P(\text{Future Correct Outcome})
}
$$

The same session may contain multiple objectives with different labels. Therefore, a strong EDA cannot stop at:

```text
Positive rows vs Negative rows
```

The central analytical question must be:

$$
\boxed{
\text{Within the same session, what objective-specific evidence distinguishes } O^+ \text{ from } O^-?
}
$$

At the same time, the transcript is ordered. Therefore, another core question is:

$$
\boxed{
\text{How does evidence and dialogue behaviour evolve through session time?}
}
$$

The final Phase-2 question is:

$$
\boxed{
\text{Which observed relationships are stable, unique, reproducible, and useful enough to inform the architecture?}
}
$$

This phase therefore has three analytical axes:

```text
DIALOGUE SEQUENCE
        ×
OBJECTIVE-SPECIFIC EVIDENCE
        ×
EXACT MULTIVARIATE VALIDATION
```

---

# 1. Evidence Base Reviewed Before Freezing This Plan

This plan was re-checked against:

- the frozen Phase-1 data-foundation specification;
- the executed Phase-1 integrity notebook and its final hard gate;
- the current Scratch Mastery roadmap;
- the current simplified main architecture;
- the mathematical architecture from evidence pack to final probability;
- the uploaded `2.2multivariate_eda.ipynb` reference notebook.

The reference multivariate notebook is useful because its strongest idea is not any one plot. Its useful analytical philosophy is:

```text
Question
→ mechanism / logic
→ direct relationship
→ conditional relationship
→ nonlinear geometry
→ interaction
→ uncertainty
→ discovery
→ independent confirmation
→ redundancy / global structure
→ final decision
```

That philosophy is retained here, but adapted to Trace the Ace rather than copied mechanically.

---

# 2. Non-Negotiable Phase-2 Boundaries

## Phase 2 WILL do

- dialogue-sequence analysis;
- event-time / within-session temporal analysis;
- role-transition analysis;
- objective-text geometry;
- fixed diagnostic objective-to-turn relevance probing;
- student vs tutor relevance separation;
- objective-specific temporal localization;
- same-session positive–negative contrast;
- objective-swap diagnostics;
- sparse-vs-dense complementarity diagnostics;
- nonlinear relationship analysis;
- conditional surfaces;
- interaction confirmation;
- fold-stability analysis;
- inference-compatibility analysis;
- architecture-role assignment;
- Phase-3 retrieval hypotheses and search ranges.

## Phase 2 WILL NOT do

```text
❌ repeat null / duplicate / schema checks
❌ re-check source files
❌ re-validate Phase-1 joins
❌ re-parse transcripts
❌ row-by-row transcript review
❌ classical ARIMA / ACF / PACF time-series modelling
❌ train or tune the production sparse retriever
❌ fine-tune the dense retriever
❌ train the Cross-Encoder
❌ build the final evidence pack
❌ train ModernBERT
❌ train the final structured branch
❌ train the evidence-confidence gate
❌ fit the final objective prior hyperparameter
❌ fit final blend weights
❌ calibrate the final model
❌ use test-set aggregates
❌ use target information to construct supposedly target-free states
```

---

# 3. Important Methodological Problems Solved in This Final Plan

The earlier draft was useful but still had several hidden risks. This final design explicitly fixes them.

## Problem A — Treating dialogue like a classical time series

Turns are ordered, but they are not regularly spaced independent time-series observations.

There are variable session lengths, timestamp ties, irregular elapsed times, multiple objectives sharing the same sequence, and a response-level target rather than a turn-level target.

Therefore:

$$
\boxed{
\text{Correct framework} = \text{event-time / sequence / longitudinal-within-session analysis}
}
$$

Two clocks will be kept:

### Turn-progress clock

$$
u_t=\frac{t}{n_{\text{turns}}-1}
$$

### Wall-time clock

$$
\tau_t=\text{timestamp}_t-\text{timestamp}_{start}
$$

Neither replaces the other.

---

## Problem B — Pseudo-replication

There are more than six million turns, but there are not six million independent outcomes.

A response label cannot be copied to every turn and then treated as millions of independent observations.

Statistical inference will respect the real analytical unit:

```text
Session analysis       → session is the unit
Response analysis      → session-objective response is the unit
Pair analysis          → same-session objective pair is the unit
Objective analysis     → objective is the macro unit
```

Bootstrap and confidence intervals must cluster at the **session** level when responses share sessions.

---

## Problem C — Sessions with many objectives dominating pairwise analysis

A session with many positive and negative objectives can generate many pair combinations.

For session $s$:

$$
N_s^{pairs}=n_s^+n_s^-
$$

Each pair will therefore receive:

$$
\boxed{
w_{pair,s}=\frac{1}{n_s^+n_s^-}
}
$$

so every mixed session contributes total weight approximately 1.

Pairwise ties will be reported separately and, when a single win-rate summary is needed, receive 0.5 credit.

---

## Problem D — Frequent objectives dominating global findings

An objective appearing hundreds of times should not automatically determine the conclusion for rare objectives.

Every important outcome relationship will therefore be reported in two ways:

```text
MICRO  → each response has equal weight
MACRO  → each objective has equal weight
```

When those disagree, the relationship is not called universally stable.

---

## Problem E — Long sessions producing artificially larger maximum relevance scores

Long sessions contain more turns. Even random similarity has more chances to generate a high maximum score.

Therefore raw `max similarity` will never be interpreted alone.

Every relevance family should also examine:

- top-1 vs top-2 margin;
- top-k concentration;
- score dispersion;
- local background score;
- role-specific concentration;
- temporal concentration;
- session-length stratification;
- objective-swap/null contrast.

A relationship that disappears after length stratification is not a robust evidence signal.

---

## Problem F — Similarity scores are not automatically comparable across objectives

Different objectives can have different score distributions.

Therefore EDA will not assume:

```text
0.80 for Objective A == 0.80 for Objective B
```

Primary analysis will use both:

```text
absolute score
relative/rank-based score within the response
score margin
score concentration
```

This is especially important for sparse vs dense comparisons.

---

## Problem G — Arbitrary sparse weights during EDA

Using a weighted combination such as

$$
\alpha TFIDF+\beta Char+\gamma Math
$$

inside EDA would already introduce a tunable retriever.

Therefore Phase 2 will first study the sparse channels separately:

```text
Word TF-IDF
Char n-gram
Math-token overlap
```

A combined sparse score may be shown only as a sensitivity analysis with a declared fixed rule. Production weights belong to Phase 3.

---

## Problem H — Calling any Tutor → Student sequence “feedback”

A tutor turn is not automatically a correction, hint, scaffold, or confirmation.

Until semantic evidence processing exists, Phase 2 will use neutral names:

```text
PRE-ANCHOR STUDENT
ANCHOR TURN
POST-ANCHOR STUDENT
```

Only later stages may assign semantic functions such as correction or scaffold.

---

## Problem I — In-session evidence is not the same thing as the target

The label represents a later/future outcome.

Therefore:

```text
Strong evidence in transcript ≠ proven mastery
Tutor help ≠ causal improvement
Student correction in-session ≠ guaranteed future positive label
```

EDA language must remain associational.

---

## Problem J — Target-informed temporal states

If target rates are used to define states and then those states are evaluated against the same target, the result is circular.

Correct rule:

```text
Predictors / trajectories → define state
Target                    → characterize frozen state afterward
```

If a threshold is target-optimized, it must be learned inside discovery folds and evaluated only on a held-out fold.

---

## Problem K — Discovery and confirmation leakage

Interesting-looking relationships can be overfit through repeated inspection.

Therefore Phase 2 will use the already frozen grouped folds as a **rotating discovery-confirmation system**.

For held-out fold $k$:

```text
Other 4 folds → discover bins / thresholds / interaction form
Fold k        → confirm only
```

Repeat for all five folds.

Final relation status depends on:

```text
direction stability
magnitude stability
shape stability
support stability
```

---

## Problem L — Multiple testing

Dozens of features and interactions can produce chance discoveries.

Therefore a relationship is not retained because of one p-value or one attractive heatmap.

Evidence hierarchy:

1. practical effect size;
2. adequate support;
3. held-out stability;
4. clustered/bootstrap uncertainty;
5. FDR control when many formal hypothesis tests are performed;
6. architecture relevance.

---

## Problem M — Trying to select the final 20–35 structured features too early

Many final structured features depend on **production retrieval and Cross-Encoder scores**, for example:

```text
student_support_max
cross_encoder_top1
retrieval_margin
tutor_minus_student
```

Those values do not exist yet in Phase 2.

Therefore Phase 2 will NOT freeze the final 20–35 feature set.

It will freeze:

```text
feature families
candidate definitions
expected roles
validation criteria
Phase-3/Phase-4 tests required
```

The final 20–35 features are selected only after production retrieval and reranking outputs exist.

---

## Problem N — Evidence-confidence gate cannot be justified before evidence scores exist

Phase 2 may identify candidate confidence concepts such as relevance concentration, sparse-dense disagreement, role disagreement, evidence dispersion, and evidence sparsity.

But it cannot prove that a neural gate is needed.

Therefore:

```text
Gate = architecture candidate
not a Phase-2 conclusion
```

Later it must beat a no-gate fusion in proper OOF ablation.

---

## Problem O — Inference-incompatible EDA features

A beautiful training analysis is useless if the feature cannot exist at test inference.

Every candidate signal must receive one of these statuses:

```text
INFERENCE_SAFE
TRAINING_ONLY_DIAGNOSTIC
REQUIRES_FOLD_SAFE_ESTIMATION
NOT_PRODUCTION_ELIGIBLE
```

Examples:

- same-session role trajectory → inference safe;
- global target mean → not inference safe;
- fold-safe objective prior → requires fold-safe estimation;
- baseline error class → training-only diagnostic.

---

# 4. Final Three-Notebook Architecture

```text
04_dialogue_sequence_dynamics.ipynb
        ↓
05_objective_evidence_geometry.ipynb
        ↓
06_exact_multivariate_architecture_validation.ipynb
        ↓
PHASE 2 FREEZE
        ↓
PHASE 3 — Production Retrieval
```

Each notebook answers one distinct question.

---

# NOTEBOOK 04 — `04_dialogue_sequence_dynamics.ipynb`

## Core Question

> **How does the tutoring dialogue evolve through event time, independent of any particular objective, and which structural dynamics may later provide reliable context or confidence information?**

This notebook is intentionally **objective-agnostic** and must not attempt mastery interpretation.

## 04.0 — Phase-2 Bootstrap

### Inputs

```text
canonical/responses.parquet
canonical/turns.parquet
canonical/sessions.parquet
canonical/objectives.parquet
frozen fold assignment
```

### It will NOT re-run

```text
null checks
duplicate checks
schema audit
source audit
turn-order audit
```

Only enough assertions to prevent accidental use of the wrong artifact version are allowed.

## 04.1 — Define the Two Temporal Coordinates

For every turn:

### Relative turn position

$$
u_t=\frac{turn\_index}{n_{turns}-1}
$$

### Elapsed wall time

$$
\tau_t=timestamp_t-timestamp_{first}
$$

### Derived descriptive quantities

```text
relative_position
elapsed_seconds
time_since_previous_turn
role
text length
token/word count
math-token count
numeric-token count
unclear flag
repeat relation
```

No target is used.

## 04.2 — Multi-Resolution Dialogue Trajectories

One arbitrary binning is fragile.

Therefore trajectories will be analyzed at:

```text
3 bins   → early / middle / late
5 bins   → medium resolution
10 bins  → detailed resolution
```

For each role and temporal bin:

```text
turn share
word/token share
math-token share
numeric-token share
[UNCLEAR] share
exact-repeat share
speaker-switch density
median response latency
```

### Main robustness question

> Does the observed temporal pattern survive 3-bin, 5-bin and 10-bin representations?

If not, it is resolution-sensitive and should not be treated as a stable feature family.

## 04.3 — Role Transition System

Model the role sequence descriptively:

$$
P(R_{t+1}=j\mid R_t=i)
$$

Core transitions:

```text
Tutor → Student
Student → Tutor
Tutor → Tutor
Student → Student
Background → Tutor
Background → Student
```

Derived sequence statistics:

```text
speaker-switch rate
student run length
tutor run length
transition entropy
role dominance
turn-taking entropy
burstiness
```

These are session-context candidates, not objective-mastery features.

## 04.4 — Structural Response Cycles

Neutral patterns:

```text
Tutor → Student
Student → Tutor → Student
Tutor → Tutor → Student
Student → Student
```

For a structural cycle, compare pre/post student behaviour:

$$
\Delta Length=Length_{post}-Length_{pre}
$$

$$
\Delta Numeric=Numeric_{post}-Numeric_{pre}
$$

$$
\Delta Math=Math_{post}-Math_{pre}
$$

$$
\Delta Novelty=Novelty_{post}-Novelty_{pre}
$$

Also examine latency, copy/repetition ratio, lexical expansion, and compression.

No semantic label such as “correction success” is assigned here.

## 04.5 — Temporal Dynamics

Candidate target-blind trajectory descriptors:

### Early-to-late slope

$$
\Delta_{EL}=X_{late}-X_{early}
$$

### Volatility

$$
Volatility=SD(X_{bin})
$$

### Temporal concentration

$$
Concentration=\frac{\max_b X_b}{\sum_b X_b+\epsilon}
$$

### Persistence

Number or fraction of consecutive bins with sustained activity.

### Entropy

$$
H=-\sum_b p_b\log(p_b)
$$

Possible dimensions:

```text
student activity
tutor activity
math activity
speaker switching
repetition
unclear speech
```

## 04.6 — Target-Blind Dialogue Archetypes

If trajectory structure supports it, use unsupervised clustering only on predictor trajectories.

Possible algorithm family:

```text
standardized trajectory vectors
→ PCA only if needed for clustering stability
→ k-means / hierarchical clustering
→ stability analysis
```

PCA is **not** a required modelling feature. It is allowed only as a technical aid if high-dimensional trajectory vectors require compression.

Cluster number must be chosen by target-free criteria such as silhouette, cluster stability, minimum support, and interpretability.

Only after the archetypes are frozen will future outcome rates be compared.

## 04.7 — Session Outcome Context

For description only:

```text
ALL_POSITIVE
ALL_NEGATIVE
MIXED
```

Compare frozen dialogue dynamics across these groups.

Interpretation rule:

> A relationship here describes **session context**, not objective-specific discrimination.

This distinction is mandatory because every objective in the same session shares the same dialogue-level features.

## 04.8 — Repetition as a Modelling Phenomenon

Phase 1 preserved repeated content. Phase 2 does not re-audit it.

Instead examine aggregate sequence patterns:

```text
Student → identical Student
Tutor → identical Tutor
Tutor text repeated later
Student text repeated after Tutor
early repetition
late repetition
short-lag repetition
long-lag repetition
```

Goal: determine whether repetition is potentially a confidence/context signal.

No rows are deleted.

## 04.9 — Long Utterance / Context-Length Behaviour

Very long utterances are already known from Phase 1.

Here the question is not whether they are valid.

The modelling question is:

```text
Where do they occur?
Which roles generate them?
Are they concentrated early/late?
Do they dominate local token budgets?
```

This informs later evidence-packing and truncation policy.

## 04.10 — Statistical Rules

No turn-level naive p-values.

Use:

```text
session-level aggregation
session bootstrap
cluster-aware confidence intervals
micro + macro summaries where relevant
```

## 04.11 — Notebook-04 Decision Registry

Every discovered relationship receives:

```text
signal_name
analytical_unit
definition
direction
nonlinearity
resolution_stability
session_bootstrap_ci
inference_status
possible_architecture_role
decision
```

Possible roles:

```text
SESSION_CONTEXT
TEMPORAL_CONTEXT
CONFIDENCE_CANDIDATE
PACKING_DIAGNOSTIC
DROP
```

## Notebook-04 Outputs

```text
04_dialogue_sequence_dynamics/
├── session_temporal_context.parquet
├── trajectory_summary.parquet
├── role_transition_summary.parquet
├── repetition_dynamics.parquet
├── dialogue_archetype_summary.parquet          # only if stable
├── dialogue_signal_registry.parquet
└── 04_findings.json
```

## Notebook-04 Gate

Notebook 04 passes when:

```text
✓ no target used to construct trajectory features/states
✓ temporal findings checked at multiple resolutions
✓ no turn-level pseudo-replication
✓ session-level uncertainty respected
✓ every retained signal has an inference-status label
✓ no semantic tutor-feedback claims were made
✓ no production retrieval/model training occurred
```

---

# NOTEBOOK 05 — `05_objective_evidence_geometry.ipynb`

## Core Question

> **For a specific learning objective, where is the relevant evidence in the session, which role carries it, how is it distributed through dialogue time, and how does that pattern differ from another objective in the same session?**

This notebook is the central Phase-2 notebook.

## 05.0 — Objective Geometry

Analyze the objective texts using target-blind text properties:

```text
word length
character length
math-token content
lexical similarity
char similarity
frozen semantic embedding similarity
```

Purpose:

```text
objective neighbourhood
dense objective families
isolated objectives
near-semantic objectives
math-heavy vs language-heavy objectives
```

No outcome label is used to construct objective clusters.

## 05.1 — Fixed Diagnostic Relevance Probes

These are **diagnostic instruments**, not the production retriever.

### Sparse Probe A

Word TF-IDF similarity.

### Sparse Probe B

Character n-gram similarity.

### Sparse Probe C

Math-token overlap.

### Dense Probe D

One pre-declared frozen Sentence-Transformer.

Rules:

```text
no target-based model selection
no target-based weight tuning
no Cross-Encoder
no fine-tuning
no learned top-K
```

If a second dense model is used, it is a sensitivity check only and cannot be selected because its outcome relationship looks better.

## 05.2 — Compute Only Within-Session Objective × Turn Scores

For response $i$:

$$
\boxed{
O_i \times \{T_t:T_t\in Session_i\}
}
$$

Never construct the global Cartesian product of all objectives with all turns.

Use session-batched/chunked processing:

```text
Parquet scan
→ session batch
→ objective batch within session
→ score turns
→ aggregate immediately
→ save compact summaries
```

Avoid retaining a giant all-pairs table unless a sampled diagnostic table is explicitly needed.

## 05.3 — Role-Specific Evidence Geometry

For each response and each probe:

```text
student_top1
student_topk_mean
tutor_top1
tutor_topk_mean
background_top1
student_tutor_gap
top1_top2_margin
score_dispersion
score_concentration
```

No one score is treated as the truth.

## 05.4 — Evidence Localization

For relevance $r_t$ at relative time $u_t$:

### Temporal centre of mass

$$
C=\frac{\sum_t r_tu_t}{\sum_t r_t+\epsilon}
$$

### Temporal spread

Weighted dispersion around $C$.

### Active evidence span

Distance between earliest and latest high-relative-relevance regions.

### Multi-peak structure

Does evidence occur in one localized region or multiple separated regions?

### Role localization

What proportion of the high-relevance mass comes from student vs tutor?

## 05.5 — Multi-Resolution Objective Relevance Trajectory

For each objective-response:

$$
R_{student}(u),\qquad R_{tutor}(u)
$$

summarized at:

```text
3 temporal bins
5 temporal bins
10 temporal bins
```

Possible target-blind descriptors:

```text
early relevance
middle relevance
late relevance
late-minus-early
relevance volatility
relevance persistence
relevance concentration
role shift through time
```

## 05.6 — Long-Session Bias Diagnostics

Because longer sessions have more opportunities for accidental high similarity, stratify all relevance metrics by:

```text
session turn count
session duration
objective count
```

A metric is downgraded if its apparent usefulness is mostly explained by session length.

Also compare:

```text
top score
top-vs-background margin
top1-top2 margin
concentration
```

The latter three are generally more robust than raw maxima.

## 05.7 — Anchor-Neighbourhood Analysis

For a strong diagnostic anchor turn:

```text
-3
-2
-1
ANCHOR
+1
+2
+3
```

Analyze role sequence, student/tutor relevance before and after, lexical novelty, math-token change, response latency, and repeat/copy ratio.

Use neutral terminology:

```text
PRE-ANCHOR
ANCHOR
POST-ANCHOR
```

No automatic claim of correction, feedback, or learning.

## 05.8 — Same-Session Positive–Negative Contrast

This is the primary controlled EDA.

For the same session:

$$
O^+,\;O^-
$$

For feature $f$:

$$
\Delta f=f(S,O^+)-f(S,O^-)
$$

Metrics:

### Weighted pairwise win rate

$$
WinRate_f=P_w(f^+>f^-)
$$

with each mixed session contributing equal total weight.

### Tie rate

$$
TieRate_f=P_w(f^+=f^-)
$$

### Median pair margin

$$
Median(\Delta f)
$$

### Reversal rate

$$
P_w(f^+<f^-)
$$

### Fold stability

Compute independently across frozen folds.

This is the strongest Phase-2 diagnostic for later pairwise training.

## 05.9 — Objective-Swap Stress Test

Keep the transcript fixed. Swap only the objective.

Question:

> Does the relevance landscape actually respond to the objective?

For objectives $O_a,O_b$ in the same session:

```text
ranking overlap
top-turn identity change
student relevance change
tutor relevance change
temporal-centre shift
role-mass shift
```

A useful objective-conditioned signal should not produce almost identical evidence for every objective in a mixed session.

## 05.10 — Sparse–Dense Complementarity

Analyze:

```text
Sparse strong / Dense weak
Dense strong / Sparse weak
Both strong
Both weak
```

Metrics:

```text
top-k overlap
rank correlation
role agreement
temporal-centre agreement
same-session pairwise direction
objective-family dependence
math-heavy vs text-heavy dependence
```

Output is not a production blend weight.

Output is:

```text
Is hybrid retrieval justified?
Where is each channel strong?
What search ranges should Phase 3 test?
```

## 05.11 — Objective Similarity × Evidence Similarity

Advanced relationship:

$$
\text{Objective Similarity} \times \text{Evidence Overlap}
$$

Investigate whether semantically close objectives retrieve almost identical evidence.

This is especially relevant when the session labels disagree.

Use aggregate groups only; no row-wise manual inspection is required.

Possible Phase-3 implication:

```text
hard-negative objective families
stronger reranking requirement
larger candidate diversity requirement
```

## 05.12 — Student–Tutor Evidence Regimes

Define regimes using **predictor-only thresholds** learned in discovery folds:

```text
Student strong / Tutor weak
Student strong / Tutor strong
Student weak / Tutor strong
Both weak
```

Then characterize outcome rates only on the held-out fold.

The purpose is to assess whether tutor-heavy relevance behaves differently from student-heavy relevance.

## 05.13 — Objective Frequency and Prior Reliability

This is not the final prior fitting stage.

Analyze:

```text
objective support size
raw outcome-rate variance
fold-to-fold variance
rare-objective instability
macro vs micro behaviour
```

For fold-safe diagnostic prior:

$$
p_o^{(-k)}=\frac{n_{o,-k}^{+}+\alpha p_{global,-k}}{n_{o,-k}+\alpha}
$$

Test a broad diagnostic grid:

```text
α ∈ {5, 10, 20, 40, 80}
```

Goal:

```text
identify stable range
identify rare-objective failure modes
identify when prior is informative vs dangerous
```

Do not freeze the final training alpha here.

## 05.14 — Objective Probe Registry

Every metric receives:

```text
signal_name
probe_family
role
absolute_vs_relative
length_sensitivity
same_session_win_rate
tie_rate
median_pair_margin
reversal_rate
micro_effect
macro_effect
fold_stability
inference_status
recommended_use
```

Possible recommended uses:

```text
RETRIEVAL_HYPOTHESIS
ROLE_SIGNAL
TEMPORAL_HYPOTHESIS
PAIRWISE_SIGNAL
CONFIDENCE_TEMPLATE
DIAGNOSTIC_ONLY
DROP
```

## Notebook-05 Outputs

```text
05_objective_evidence_geometry/
├── objective_geometry.parquet
├── objective_probe_summary.parquet
├── objective_temporal_summary.parquet
├── same_session_pair_diagnostics.parquet
├── objective_swap_diagnostics.parquet
├── sparse_dense_complementarity.parquet
├── objective_prior_diagnostics.parquet
├── objective_signal_registry.parquet
└── 05_retrieval_hypotheses.json
```

## Notebook-05 Gate

Notebook 05 passes when:

```text
✓ production retriever was not trained
✓ sparse channels were not outcome-tuned
✓ dense probe was fixed before target comparison
✓ objective × turn scoring stayed within session
✓ long-session score inflation was explicitly analyzed
✓ same-session pair metrics used per-session weighting
✓ micro and macro objective results were both considered
✓ objective-swap diagnostics were completed
✓ no semantic feedback labels were assumed
✓ only candidate search ranges, not final K/weights, were produced
```

---

# NOTEBOOK 06 — `06_exact_multivariate_architecture_validation.ipynb`

## Core Question

> **Which Phase-2 signals are reproducible, non-redundant, nonlinear, conditionally useful, inference-compatible, and sufficiently architecture-relevant to justify carrying forward?**

This notebook turns EDA findings into a **model-development blueprint**. It does not train the final model.

## 06.0 — Consolidated Candidate Registry

Combine candidates from Notebook 04 and 05.

Feature families:

```text
A. Session context
B. Dialogue temporal dynamics
C. Objective relevance strength
D. Role contrast
E. Objective temporal localization
F. Evidence concentration / dispersion
G. Sparse–dense agreement
H. Same-session discriminators
I. Prior context
```

Do not pre-label them as final features.

## 06.1 — Explicit Analytical Unit for Every Signal

Every analysis must state:

```text
SESSION
RESPONSE
SAME_SESSION_PAIR
OBJECTIVE
```

No result is accepted without a declared analytical unit.

## 06.2 — Discovery Layer

High-recall discovery may use:

```text
risk / outcome curves
effect size
mutual information
rank association
same-session discrimination
conditional surfaces
```

Weak-looking signals are not immediately dropped if architecture logic suggests a conditional role.

## 06.3 — Exact Typed Confirmation

Use methods appropriate to the variable type.

Examples:

```text
continuous × continuous → Pearson + Spearman
binary × continuous     → point-biserial + effect size
binary × binary         → Phi
categorical             → Cramér's V / conditional rate difference
nonlinear signal        → binned / spline-shaped held-out curve
```

The goal is not to maximize the number of statistics. The goal is to avoid using one generic correlation measure for incompatible relationships.

## 06.4 — Rotating Discovery–Confirmation Protocol

For fold $k$:

```text
Discovery    = all folds except k
Confirmation = fold k
```

Anything learned from target:

```text
bin edges
thresholds
state cutoffs
interaction cutoffs
```

must be learned only in Discovery.

Final confirmation table:

```text
fold
direction
effect_size
shape
support
confirmation_status
```

Final relationship status:

```text
STABLE
CONTEXTUAL
NONLINEAR_STABLE
OBJECTIVE_DEPENDENT
UNSTABLE
INSUFFICIENT_SUPPORT
DROP
```

## 06.5 — Nonlinear Geometry

For serious candidates, classify the held-out shape:

```text
MONOTONIC_POSITIVE
MONOTONIC_NEGATIVE
THRESHOLD
TAIL_ONLY
U_SHAPED
INVERTED_U
STEPWISE
NON_MONOTONIC
FLAT
```

Do not assume linearity merely because Pearson correlation is small.

## 06.6 — Architecture-Driven Conditional Surfaces

Only a controlled set of interactions will be tested.

Priority surfaces:

```text
Student relevance × Tutor relevance
Evidence strength × Evidence dispersion
Early evidence × Late evidence
Student–Tutor gap × Late evidence
Evidence concentration × Student evidence
Sparse evidence × Dense evidence
Session context × Objective evidence
Fold-safe prior × Objective evidence
```

For each cell:

```text
support
outcome rate
risk difference
uncertainty
```

Minimum support is mandatory.

## 06.7 — Interaction Confirmation

For selected pair $x_1,x_2$:

### Additive confirmation model

$$
logit(p)=\beta_0+\beta_1x_1+\beta_2x_2
$$

### Interaction confirmation model

$$
logit(p)=\beta_0+\beta_1x_1+\beta_2x_2+\beta_3x_1x_2
$$

These are **diagnostic confirmation models**, not production candidates.

Evaluate on held-out fold:

$$
\Delta LL=LL_{additive}-LL_{interaction}
$$

Retain an interaction hypothesis only when:

```text
held-out ΔLogLoss > practical threshold
adequate support
stable interaction direction
not driven by one objective
not driven by one fold
```

If many formal tests are performed, apply FDR control.

## 06.8 — Dependency / Redundancy Communities

Build a feature-dependency graph using appropriate associations.

Purpose:

```text
find redundant clusters
find complementary signals
find bridge variables
avoid 10 versions of the same temporal feature
```

Example communities:

```text
ROLE EVIDENCE
TEMPORAL LOCALIZATION
SESSION ACTIVITY
EVIDENCE CONFIDENCE
SPARSE/DENSE AGREEMENT
OBJECTIVE PRIOR
```

A representative is chosen because of stability + architecture role, not simply because it has the largest target correlation.

## 06.9 — Same-Session Discrimination as a Separate Axis

Every response-level candidate is evaluated twice.

### Global outcome relation

Does it separate positive and negative responses overall?

### Same-session relation

Does it separate $O^+$ and $O^-$ inside the same session?

This allows a critical classification:

### High global / weak same-session

```text
SESSION_CONTEXT
PRIOR_CONTEXT
```

### Strong same-session

```text
OBJECTIVE_DISCRIMINATOR
PAIRWISE_CANDIDATE
```

### Mostly reliability-related

```text
CONFIDENCE_TEMPLATE
```

This prevents general-session signals from being mislabeled as mastery evidence.

## 06.10 — Baseline Failure-Conditioned Analysis

If a validated grouped-OOF baseline file is available, use it only as a **diagnostic lens**.

Groups:

```text
confident false positive
confident false negative
collapsed mixed session
reversed pair
correct high-confidence control
```

Question:

> Does a candidate signal carry information exactly where the baseline fails?

Baseline predictions are never used as model inputs.

If the OOF artifact is not available or not perfectly aligned to frozen folds, skip this section rather than reconstructing it approximately.

## 06.11 — Robustness Regimes

Training-only subgroup diagnostics:

```text
rare objectives
frequent objectives
math-heavy objectives
language-heavy objectives
short sessions
long sessions
low-objective-count sessions
high-objective-count sessions
student-dominant sessions
tutor-dominant sessions
evidence-localized responses
evidence-diffuse responses
```

A feature that works only in one narrow regime is marked contextual, not universally strong.

## 06.12 — Inference-Compatibility Gate

Every candidate must answer:

### Can it be computed from one test session and its objective?

If yes:

```text
INFERENCE_SAFE
```

### Does it require learned target statistics?

If yes:

```text
REQUIRES_FOLD_SAFE_ESTIMATION
```

### Does it require labels or OOF errors?

If yes:

```text
TRAINING_ONLY_DIAGNOSTIC
```

### Does it require aggregate statistics across unrelated test sessions?

Then:

```text
NOT_PRODUCTION_ELIGIBLE
```

This gate is mandatory before any signal is handed to the model-development phase.

## 06.13 — Architecture Decision Matrix

Final EDA output does **not** say:

```text
Final feature #1
Final feature #2
...
Final feature #30
```

Instead it produces:

| Signal Family | EDA Evidence | Phase-3/4 Role | Status |
|---|---|---|---|
| Student relevance strength | pairwise stable | retrieval/structured | carry |
| Tutor relevance strength | conditional | tutor/help | carry |
| Late relevance | stable | temporal feature | carry |
| Evidence dispersion | reliability signal | gate candidate | carry |
| Sparse–dense disagreement | uncertainty | gate candidate | carry |
| Session duration | global only | context | contextual |
| Objective prior | stable but risk-prone | fold-safe prior | carry |
| Redundant temporal variant | duplicate information | none | drop |
| Unstable interaction | fold-specific | none | drop |

## 06.14 — Phase-3 Retrieval Handoff

Phase 2 should provide **hypotheses and ranges**, not final retrieval hyperparameters.

Example:

```text
Sparse:
- word and char appear complementary
- math overlap matters primarily for math-heavy objective family

Dense:
- strongest benefit in paraphrastic objective families

Candidate pool:
- evidence appears localized in most sessions
- long/diffuse sessions need larger candidate allowance

Role:
- student-only retrieval misses useful context
- tutor quota may be necessary

Reranking:
- objective-swap ambiguity identifies hard negatives
```

Possible output ranges:

```text
Sparse top-K search range  : e.g. 5–20
Dense top-K search range   : e.g. 5–20
Union-size search range    : data-derived range
Role quota candidates      : none / soft quota / minimum student
Anchor window candidates   : ±1 / ±2 / ±3
```

Exact values are Phase-3 experiments.

## Notebook-06 Outputs

```text
06_exact_multivariate_architecture_validation/
├── consolidated_signal_registry.parquet
├── fold_confirmation_summary.parquet
├── nonlinear_shape_registry.parquet
├── conditional_surface_summary.parquet
├── interaction_registry.parquet
├── dependency_communities.parquet
├── same_session_discrimination.parquet
├── inference_compatibility.parquet
├── robustness_summary.parquet
├── architecture_decision_matrix.parquet
├── retrieval_design_hypotheses.json
├── structured_feature_family_spec.json
└── phase2_gate.json
```

## Notebook-06 Gate

Notebook 06 passes when:

```text
✓ every candidate has an analytical unit
✓ target-derived choices were cross-fitted
✓ global and same-session discrimination are separated
✓ frequent objectives do not silently dominate all conclusions
✓ pair-heavy sessions are session-normalized
✓ nonlinearity is tested rather than assumed
✓ interactions require held-out confirmation
✓ redundant signals are grouped
✓ every candidate has an inference-compatibility status
✓ no final structured feature count is prematurely frozen
✓ no production model was trained
✓ Phase-3 hypotheses are explicit and testable
```

---

# 5. Standard Investigation Template for All Three Notebooks

Every major analysis section should follow:

```text
Research Question
        ↓
Why It Matters for Architecture
        ↓
Analytical Unit
        ↓
Predictor Definition
        ↓
Target-Blind Construction Rule
        ↓
Method
        ↓
Evidence
        ↓
Uncertainty / Stability
        ↓
Interpretation
        ↓
Limitation
        ↓
Architecture Decision
```

This prevents “plot-first EDA”.

---

# 6. Visualization Strategy

The goal is not to maximize plots. Each figure must answer one decision question.

Recommended plot families:

### Dialogue trajectory

```text
x = relative session position
y = role/activity statistic
```

### Objective relevance trajectory

```text
x = relative session position
y = relevance
line = student / tutor
```

### Conditional surface

```text
x = signal A
y = signal B
cell/color = held-out outcome rate
```

### Pairwise margin distribution

```text
x = f(O+) - f(O-)
```

### Fold stability forest

```text
effect size by fold + confidence interval
```

### Sparse–dense agreement map

```text
x = sparse signal
y = dense signal
color = same-session discrimination / regime
```

### Dependency network

Nodes = candidate signals  
Edges = strong redundancy / association

Avoid decorative charts that do not change an architecture decision.

---

# 7. Metrics That Matter Most in Phase 2

## Overall relationship metrics

```text
risk difference
relative risk where sensible
effect size
Spearman/Pearson where appropriate
mutual information
cluster-aware confidence interval
```

## Same-session metrics

```text
weighted pairwise win rate
tie rate
median margin
reversal rate
mixed-session coverage
fold stability
```

## Objective-conditioned metrics

```text
student relevance strength
tutor relevance strength
student–tutor gap
temporal centre
temporal dispersion
evidence concentration
objective-swap sensitivity
sparse–dense agreement
```

## Stability metrics

```text
direction stability
magnitude stability
shape stability
objective-macro stability
fold stability
regime stability
```

---

# 8. What EDA Is Allowed to Conclude

Valid conclusions:

> Student-heavy objective relevance is consistently associated with higher future-correct outcomes inside mixed sessions.

> Tutor-heavy relevance without corresponding student relevance is a possible assistance/context signal rather than direct mastery evidence.

> Evidence is often temporally localized, suggesting a retrieval architecture should preserve local neighbourhood context.

> Sparse and dense probes recover complementary evidence in different objective families.

Invalid conclusions at this phase:

> Tutor correction causes learning.

> This is the final retrieval K.

> This is the final 30-feature set.

> The confidence gate definitely improves performance.

> A Cross-Encoder is definitely necessary because the diagnostic probe is imperfect.

Those require later controlled experiments.

---

# 9. Final Phase-2 Outputs and Handoff

At Phase-2 freeze, we should know:

### Dialogue

```text
Which temporal/session dynamics are real?
Which are context-only?
Which are stable across trajectory resolution?
```

### Objective Evidence

```text
Where does objective-specific evidence occur?
Which role carries it?
How localized or diffuse is it?
Does objective swapping meaningfully change evidence?
Do sparse and dense channels complement each other?
```

### Same-Session Discrimination

```text
Which evidence relationships distinguish O+ from O-?
Which signals only reflect general session quality?
Which candidate signals justify pairwise learning?
```

### Architecture

```text
Which signal families feed retrieval?
Which signal families are structured-feature candidates?
Which are gate candidates?
Which are prior/context signals?
Which should be dropped?
```

### Phase-3 Search Space

```text
candidate retrieval K ranges
role-quota hypotheses
window-size ranges
hard-negative families
sparse/dense complementarity hypotheses
reranking hypotheses
```

---

# 10. Phase-2 Final Hard Gate

Phase 2 is complete only if all conditions are satisfied:

| Gate | Requirement |
|---|---|
| Data boundary | No Phase-1 integrity work repeated |
| Temporal validity | Event-time analysis, not classical time-series assumptions |
| Hierarchy validity | No turn-level pseudo-replication |
| Pair weighting | High-objective-count sessions cannot dominate |
| Objective weighting | Micro and macro findings both reported |
| Target blindness | States/probes built without target leakage |
| Discovery/confirmation | Target-informed choices cross-fitted |
| Nonlinearity | Important signals checked beyond simple linear correlation |
| Interaction validity | Held-out confirmation required |
| Long-session bias | Relevance maxima not interpreted without length-aware diagnostics |
| Objective conditioning | Objective-swap test completed |
| Same-session discrimination | Positive–negative pair analysis completed |
| Inference safety | Every candidate classified for inference compatibility |
| Architecture boundary | No final retriever / CE / ModernBERT training |
| Feature boundary | Final 20–35 feature set not frozen prematurely |
| Phase-3 handoff | Explicit, testable retrieval hypotheses produced |

Final flag:

```text
PHASE_2_ADVANCED_DIAGNOSTICS_READY = TRUE
```

Only then:

```text
PHASE 3
→ Sparse Retrieval
→ Dense Retrieval
→ Candidate Union
→ Retrieval Audit
→ Cross-Encoder Reranking
```

---

# 11. Final Three-Notebook Summary

```text
┌──────────────────────────────────────────────────────────────┐
│ 04_dialogue_sequence_dynamics.ipynb                         │
│                                                              │
│ WHAT DOES THE DIALOGUE DO OVER TIME?                         │
│                                                              │
│ event-time                                                   │
│ role transitions                                             │
│ trajectories                                                 │
│ structural response cycles                                   │
│ repetition dynamics                                          │
│ session context                                              │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 05_objective_evidence_geometry.ipynb                         │
│                                                              │
│ WHERE IS THE EVIDENCE FOR THIS OBJECTIVE?                    │
│                                                              │
│ fixed diagnostic probes                                      │
│ student vs tutor evidence                                    │
│ temporal localization                                        │
│ same-session O+ vs O-                                        │
│ objective swap                                                │
│ sparse-dense complementarity                                 │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│ 06_exact_multivariate_architecture_validation.ipynb          │
│                                                              │
│ WHICH RELATIONSHIPS SURVIVE EXACT VALIDATION?                │
│                                                              │
│ nonlinear geometry                                           │
│ conditional surfaces                                         │
│ interactions                                                 │
│ rotating confirmation                                        │
│ redundancy communities                                       │
│ inference compatibility                                      │
│ architecture decision matrix                                 │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
                     PHASE 2 FROZEN
                               │
                               ▼
                  PHASE 3 — RETRIEVAL
```

---

# 12. Final Design Principle

The Phase-2 EDA is not being built to look sophisticated.

It is being built to answer one practical modelling question:

$$
\boxed{
\text{What evidence exists in this dialogue for this objective,}
}
$$

$$
\boxed{
\text{how does that evidence evolve through the session,}
}
$$

$$
\boxed{
\text{and which relationships survive enough control to deserve a place in the architecture?}
}
$$

That is the standard by which every section, figure, metric, and derived signal should be judged.

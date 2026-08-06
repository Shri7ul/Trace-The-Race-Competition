# Step 5 — Same-Session Objective Discrimination Analysis

এই Step-এর মূল কাজ হলো:

> **একই session-এর ভেতরে model কেন একটি correct objective এবং একটি incorrect objective-কে পরিষ্কারভাবে আলাদা করতে পারছে না—সেটি খুঁজে বের করা।**

আগের analysis-এ আমরা ইতোমধ্যে দেখেছি:

* model-এর prediction প্রায় সম্পূর্ণ session-level;
* objective বদলালেও prediction খুব অল্প বদলায়;
* mixed-label session-এ correct ও incorrect objective প্রায় একই probability পায়;
* model কিছু objective সঠিকভাবে rank করলেও probability difference খুব ছোট থাকে। 
* Collapse pair-এ correct ও incorrect objective প্রায় একই SHAP/contribution pattern পেয়েছে। 

তাই Step 5-এর কাজ আবার শুধু **“collapse আছে”** বলা নয়।

Step 5-এর আসল প্রশ্ন:

> **Collapse কোথায় বেশি হচ্ছে, কতটা গুরুতর, কোন ধরনের session-এ হচ্ছে, model কখন correct ranking করছে, কখন উল্টো ranking করছে এবং কোন cases আমাদের পরবর্তী model design-এর জন্য সবচেয়ে গুরুত্বপূর্ণ?**

---

# ১. প্রথমে প্রয়োজনীয় শব্দগুলোর অর্থ

## Session কী?

একটি `session` হলো tutor ও student-এর একটি সম্পূর্ণ tutoring conversation।

উদাহরণ:

```text
Session 101

Tutor: What is 3 × 4?
Student: 12.
Tutor: Why?
Student: Because 4 + 4 + 4 = 12.
```

এই একই conversation থেকে একাধিক learning objective evaluate করা হতে পারে।

---

## Learning objective কী?

Learning objective বলতে বোঝায় student কোন নির্দিষ্ট skill বা concept শিখেছে কি না।

উপরের session-এ objective হতে পারে:

```text
Objective A:
Student can calculate multiplication.

Objective B:
Student can explain multiplication as repeated addition.

Objective C:
Student can justify an answer independently.
```

একই transcript ব্যবহার করলেও objectiveগুলোর label আলাদা হতে পারে।

```text
Objective A → Correct
Objective B → Correct
Objective C → Incorrect
```

---

## Same-session objective বলতে কী বোঝায়?

একই `session_id`-এর অধীনে থাকা বিভিন্ন objective-কে same-session objectives বলা হচ্ছে।

```text
Session 101
├── Objective A
├── Objective B
└── Objective C
```

এগুলোর transcript একই, কিন্তু learning objective এবং target label আলাদা।

---

## Mixed-label session কী?

যে session-এর মধ্যে অন্তত একটি correct এবং অন্তত একটি incorrect objective আছে, সেটি mixed-label session।

উদাহরণ:

```text
Session 101

Objective A → 1
Objective B → 1
Objective C → 0
```

এখানে:

```text
1 = correct
0 = incorrect
```

এটি mixed-label session, কারণ একই session-এ দুই ধরনের label আছে।

অন্যদিকে:

```text
Objective A → 1
Objective B → 1
Objective C → 1
```

এটি mixed-label নয়। এটি all-positive বা uniform-label session।

Step 5-এর সবচেয়ে গুরুত্বপূর্ণ population হবে mixed-label sessions। কারণ এখানেই model-কে একই transcript দেখে objective অনুযায়ী prediction আলাদা করতে হয়।

---

## Discrimination কী?

Discrimination মানে হলো model দুই ধরনের case আলাদা করতে পারছে কি না।

আমাদের ক্ষেত্রে:

> Model কি একই session-এর correct objective-কে incorrect objective-এর চেয়ে বেশি probability দিতে পারছে?

উদাহরণ:

```text
Correct objective probability   = 0.80
Incorrect objective probability = 0.40
```

এখানে discrimination ভালো।

কিন্তু:

```text
Correct objective probability   = 0.72
Incorrect objective probability = 0.71
```

Ordering সঠিক হলেও discrimination দুর্বল।

আর:

```text
Correct objective probability   = 0.60
Incorrect objective probability = 0.78
```

এখানে discrimination ভুল। Model incorrect objective-কে বেশি probability দিয়েছে।

---

## Objective collapse কী?

যখন একই session-এর correct এবং incorrect objectives প্রায় একই probability পায়, তখন সেটিকে objective collapse বলছি।

উদাহরণ:

```text
Correct objective   → 0.704
Incorrect objective → 0.699
```

Probability difference মাত্র:

```text
0.704 − 0.699 = 0.005
```

অর্থাৎ objective বদলানোর পরও model প্রায় একই judgement দিচ্ছে।

আগের analysis অনুযায়ী এই collapse baseline-এর একটি stable সমস্যা। 

---

## OOF prediction কী?

OOF অর্থ:

```text
Out-of-Fold Prediction
```

প্রতিটি row-এর prediction এমন model দিয়ে তৈরি হয়েছে, যেটি training-এর সময় ওই row বা ওই row-এর session দেখেনি।

সহজভাবে:

```text
Row A-এর prediction
→ এমন fold model দিয়েছে
→ যে model Row A দিয়ে train হয়নি
```

এটি fair evaluation।

Step 5-এ original training probability বা single holdout prediction নয়, আমাদের saved five-fold OOF prediction ব্যবহার করতে হবে।

Planned artifact structure অনুযায়ী OOF file থাকবে:

```text
baselineanalysis/
└── 02_oof_analysis/
    └── word_logistic_oof.parquet
```

Step 5-এর output-এর planned destination হলো `05_session_objective_analysis`। 

---

# ২. Step 5-এর precise research objective

আমাদের research objective হবে:

> **To identify when, where, and how the baseline fails to distinguish correct and incorrect learning objectives within the same tutoring session.**

সহজ বাংলায়:

> একই conversation-এর মধ্যে কোন objective student বুঝেছে এবং কোনটি বুঝেনি—baseline কোন পরিস্থিতিতে আলাদা করতে পারে এবং কোন পরিস্থিতিতে পারে না, সেটি খুঁজে বের করা।

---

# ৩. Step 5-এর research questions

Step 5-এ সাতটি main question থাকবে।

## Research Question 1

> আমাদের dataset-এ কতগুলো session objective discrimination পরীক্ষা করার উপযুক্ত?

এখানে আমরা বের করব:

```text
Total sessions
Multi-objective sessions
Mixed-label sessions
Mixed-label responses
Positive objectives
Negative objectives
Possible positive-negative pairs
```

---

## Research Question 2

> Correct objectives সাধারণভাবে incorrect objectives-এর চেয়ে বেশি probability পাচ্ছে কি?

এখানে pairwise ranking পরীক্ষা হবে।

---

## Research Question 3

> Probability ordering সঠিক হলেও separation বা margin যথেষ্ট বড় কি?

Model correct objective-কে সামান্য বেশি probability দিলেও practical discrimination দুর্বল হতে পারে।

---

## Research Question 4

> কতগুলো session-এ objective collapse হচ্ছে?

Collapse শুধু একটি fixed threshold দিয়ে নয়, continuous margin distribution এবং একাধিক threshold দিয়ে দেখব।

---

## Research Question 5

> কতগুলো session-এ model completely reversed?

অর্থাৎ incorrect objective-এর probability correct objective-এর চেয়ে বেশি।

---

## Research Question 6

> Collapse কোন ধরনের session-এ বেশি?

প্রথমে limited structural factors দেখব:

* session-এ objective সংখ্যা;
* transcript length;
* positive এবং negative objectives-এর সংখ্যা;
* student/tutor text balance;
* baseline confidence level।

---

## Research Question 7

> কোন actual sessions manual review এবং future model design-এর জন্য সবচেয়ে গুরুত্বপূর্ণ?

আমরা representative case বের করব:

* severe collapse;
* severe reversal;
* successful discrimination;
* high-confidence incorrect objective;
* many-objective difficult session।

---

# ৪. Step 5-এর hypotheses

Hypothesis মানে হলো analysis শুরু করার আগে আমাদের testable expectation।

## H1 — Session-level collapse hypothesis

> Mixed-label sessions-এর একটি বড় অংশে positive এবং negative objectives প্রায় একই probability পাবে।

আগের findings এই expectation support করে। 

---

## H2 — Weak-margin hypothesis

> Model correct objective-কে অনেক ক্ষেত্রে higher probability দেবে, কিন্তু probability margin খুব ছোট থাকবে।

অর্থাৎ ranking কিছুটা correct, separation দুর্বল।

---

## H3 — Reversal hypothesis

> একটি meaningful subset-এ incorrect objective correct objective-এর চেয়ে বেশি probability পাবে।

এটি simple collapse-এর চেয়ে বেশি serious failure।

---

## H4 — Complexity hypothesis

> একটি session-এ objective সংখ্যা বাড়লে discrimination কঠিন হতে পারে।

কারণ একই long transcript-এর মধ্যে বেশি objective আলাদা করতে হচ্ছে।

---

## H5 — Transcript-dominance hypothesis

> Long transcript বা tutor-heavy session-এ objective-specific margin ছোট হতে পারে।

তবে এটি hypothesis; result দেখার আগে conclusion নয়।

---

## H6 — Confidence-risk hypothesis

> High session-level confidence থাকা mixed-label session-এ incorrect objectives-এর false-positive risk বেশি হবে।

---

## H7 — Equal-session evaluation hypothesis

> Pair-level analysis কিছু বড় session দ্বারা dominated হতে পারে; sessionগুলোকে equal weight দিলে result কিছুটা বদলাতে পারে।

এটি methodologicalভাবে গুরুত্বপূর্ণ।

---

# ৫. কোন data প্রয়োজন?

নতুন notebook-এ Step 5-এর জন্য খুব বেশি artifact লাগবে না।

## OOF prediction file থেকে

প্রয়োজন:

```text
response_id
session_id
fold
target
oof_probability
learning_objective
```

Column-এর exact নাম existing file দেখে ব্যবহার করতে হবে। যেমন probability column হয়তো:

```text
oof_probability
prediction
predicted_probability
```

হতে পারে। আমরা guess করে column তৈরি করব না।

---

## Metadata/master dataset থেকে

OOF file-এ না থাকলে merge করে নিতে হবে:

```text
transcript
student_text
tutor_text
learning_objective
```

সম্ভাব্য source:

```text
Trace-The-Race-Dataset/
└── outputs/
    └── 03_master_dataset/
        └── master_train.parquet
```

অথবা enriched metadata file:

```text
05_feature_engineering/
├── train_metadata.parquet
└── validation_metadata.parquet
```

তবে সবচেয়ে গুরুত্বপূর্ণ বিষয়:

> OOF rows এবং metadata merge করতে হবে stable unique key দিয়ে, preferably `response_id`।

Row order ধরে merge করা যাবে না।

---

# ৬. Step 5-এ তিনটি analysis unit থাকবে

এটি না বুঝলে পুরো analysis confusing হয়ে যাবে।

## Unit 1 — Response-level

প্রতিটি row একটি:

```text
Session × Objective
```

combination।

উদাহরণ:

| session | objective      | target | probability |
| ------- | -------------- | -----: | ----------: |
| S1      | Multiplication |      1 |        0.74 |
| S1      | Explanation    |      0 |        0.71 |
| S1      | Reasoning      |      1 |        0.73 |

এটি response-level table।

---

## Unit 2 — Session-level

একটি session-এর সব objectives aggregate করে একটি row বানানো হবে।

উদাহরণ:

| session | objectives | positive | negative | session margin |
| ------- | ---------: | -------: | -------: | -------------: |
| S1      |          3 |        2 |        1 |          0.025 |

Session-level analysis বলবে session হিসেবে model কতটা discriminate করেছে।

---

## Unit 3 — Pair-level

একই mixed-label session-এর প্রতিটি correct objective এবং incorrect objective নিয়ে pair তৈরি হবে।

উদাহরণ:

```text
Positive objective A
vs
Negative objective C

Positive objective B
vs
Negative objective C
```

যদি একটি session-এ:

```text
2 positive objectives
3 negative objectives
```

থাকে, তাহলে pair হবে:

```text
2 × 3 = 6 pairs
```

এটিকে Cartesian positive-negative pairing বলা যায়।

সহজভাবে:

> প্রতিটি correct objective-কে প্রতিটি incorrect objective-এর সঙ্গে compare করা।

---

# ৭. Analysis Part A — Data integrity and population audit

এটি ছোট হবে, কিন্তু খুব গুরুত্বপূর্ণ।

## আমরা check করব

```text
One response_id = one row
Missing target নেই
Missing probability নেই
Probability 0 থেকে 1-এর মধ্যে
Session ID missing নয়
Target শুধু 0 বা 1
OOF fold valid
Duplicate session-objective rows আছে কি না
```

## কেন প্রয়োজন?

কারণ duplicate row থাকলে pair count ভুল হবে।

Missing probability থাকলে margin ভুল হবে।

Wrong merge হলে একই transcript-এর সঙ্গে অন্য objective যুক্ত হয়ে যেতে পারে।

## এই section-এর final table

| Check               | Expected |
| ------------------- | -------- |
| Unique response ID  | True     |
| Missing target      | 0        |
| Missing probability | 0        |
| Probability range   | 0–1      |
| Invalid targets     | 0        |
| Missing session ID  | 0        |

এই table pass না করলে Step 5 analysis শুরু করা যাবে না।

---

# ৮. Analysis Part B — Session population breakdown

প্রথমে প্রতিটি session সম্পর্কে তিনটি count বের করব:

```text
n_objectives
n_positive
n_negative
```

## `n_objectives`

Session-এ মোট কয়টি objective আছে।

## `n_positive`

কয়টি objective-এর target `1`।

## `n_negative`

কয়টি objective-এর target `0`।

## Session categories

প্রতিটি session-কে চার ভাগে ভাগ করা যায়:

```text
Single-objective
All-positive
All-negative
Mixed-label
```

### Single-objective

শুধু একটি objective আছে।

এগুলো same-session discrimination-এর জন্য usable নয়।

### All-positive

একাধিক objective আছে, কিন্তু সব target `1`।

এখানে positive-negative comparison সম্ভব নয়।

### All-negative

একাধিক objective আছে, কিন্তু সব target `0`।

এখানেও pairwise positive-negative comparison সম্ভব নয়।

### Mixed-label

কমপক্ষে একটি `1` এবং একটি `0` আছে।

এটাই Step 5-এর primary research population।

## Final population summary

আমরা দেখাব:

| Population      | Sessions | Responses | Share |
| --------------- | -------: | --------: | ----: |
| All sessions    |      ... |       ... |  100% |
| Multi-objective |      ... |       ... |   ... |
| Mixed-label     |      ... |       ... |   ... |
| All-positive    |      ... |       ... |   ... |
| All-negative    |      ... |       ... |   ... |

## কেন গুরুত্বপূর্ণ?

কারণ Step 5-এর result পুরো dataset-এর জন্য নয়।

এটি মূলত:

> **Mixed-label, multi-objective sessions-এর জন্য।**

Report-এ এই scope পরিষ্কার না করলে reader ভুলভাবে মনে করতে পারে সব session-এর উপর pairwise result হয়েছে।

---

# ৯. Analysis Part C — Positive–negative objective pair table

Mixed-label session থেকে pair table বানানো হবে।

## Pair table-এর প্রতিটি row

```text
session_id
positive_response_id
negative_response_id
positive_objective
negative_objective
positive_probability
negative_probability
probability_margin
ranking_result
pair_loss
```

---

## Positive probability

Correct objective-এর predicted probability।

```text
p_positive
```

---

## Negative probability

Incorrect objective-এর predicted probability।

```text
p_negative
```

---

## Probability margin

সবচেয়ে গুরুত্বপূর্ণ metric:

[
\text{margin}
=============

## p_{\text{positive}}

p_{\text{negative}}
]

### Example 1 — ভালো discrimination

```text
p_positive = 0.82
p_negative = 0.43

margin = 0.39
```

এটি ভালো।

### Example 2 — Weak discrimination

```text
p_positive = 0.72
p_negative = 0.70

margin = 0.02
```

Ranking ঠিক, separation দুর্বল।

### Example 3 — Collapse

```text
p_positive = 0.704
p_negative = 0.701

margin = 0.003
```

দুই objective প্রায় একই probability পেয়েছে।

### Example 4 — Reversal

```text
p_positive = 0.61
p_negative = 0.78

margin = -0.17
```

Negative margin মানে model ভুল objective-কে higher probability দিয়েছে।

---

# ১০. Pairwise ranking accuracy

## Definition

প্রতি pair-এর জন্য:

```text
Correct objective probability > Incorrect objective probability
```

হলে ranking correct।

## Formula

[
\text{Pairwise Accuracy}
========================

\frac{\text{Correctly ordered positive-negative pairs}}
{\text{Total positive-negative pairs}}
]

## Example

১০০টি pair-এর মধ্যে:

```text
68টি pair-এ positive objective higher
32টি pair-এ negative objective higher
```

তাহলে:

```text
Pairwise ranking accuracy = 68%
Reversal rate = 32%
```

আগের analysis-এ overall within-session pairwise accuracy প্রায় `67.93%` পাওয়া গেছে। এর মানে objective signal পুরোপুরি absent নয়, কিন্তু প্রায় এক-তৃতীয়াংশ pair reversed হয়েছিল। 

## Tie কীভাবে handle করব?

যদি probability exact equal হয়:

```text
p_positive = p_negative
```

তাহলে tie-কে `0.5` credit দেওয়া যেতে পারে।

তবে floating-point probability exact equal সাধারণত rare।

---

# ১১. Pairwise accuracy একা কেন যথেষ্ট নয়?

ধরুন:

```text
Correct objective   = 0.701
Incorrect objective = 0.700
```

Ranking technically correct।

কিন্তু probability difference:

```text
0.001
```

এটি meaningful separation নয়।

তাই দুটো metric একসঙ্গে দেখতে হবে:

```text
Pairwise accuracy
+
Probability margin
```

Pairwise accuracy direction বলে।

Margin separation-এর strength বলে।

---

# ১২. Analysis Part D — Margin distribution

শুধু average margin দেখব না।

আমরা দেখব:

```text
Mean margin
Median margin
25th percentile
75th percentile
Negative-margin share
Near-zero margin share
Strong-positive margin share
```

## Mean margin

সব margin যোগ করে pair count দিয়ে ভাগ।

Outlier দ্বারা প্রভাবিত হতে পারে।

## Median margin

Marginগুলো ছোট থেকে বড় সাজালে মাঝের value।

এটি extreme values দ্বারা কম প্রভাবিত হয়।

## Percentile কী?

ধরুন 25th percentile margin `-0.01`।

এর অর্থ:

> ২৫% pair-এর margin `-0.01` বা তার নিচে।

75th percentile `0.05` হলে:

> ৭৫% pair-এর margin `0.05` বা তার নিচে।

## কেন median গুরুত্বপূর্ণ?

কিছু session-এ margin খুব বড় হলে mean ভালো দেখাতে পারে। কিন্তু অধিকাংশ pair-এর separation ছোট হতে পারে।

আগের analysis-এ collapse pair-এর median margin non-collapse pair-এর তুলনায় অনেক ছোট ছিল। 

---

# ১৩. Collapse definition

Collapse-কে শুধু binary truth হিসেবে দেখা উচিত নয়।

প্রথমে আমরা margin continuous variable হিসেবে বিশ্লেষণ করব।

তারপর case extraction-এর জন্য operational thresholds ব্যবহার করব।

## Recommended thresholds

```text
Severe collapse:
|margin| < 0.01

Moderate collapse:
|margin| < 0.02

Broad weak separation:
|margin| < 0.05
```

## Absolute margin কেন?

```text
|margin|
```

মানে margin-এর absolute বা sign-বিহীন size।

উদাহরণ:

```text
margin = +0.01 → absolute = 0.01
margin = -0.01 → absolute = 0.01
```

দুটিই near-equal prediction নির্দেশ করে।

তবে reversed pair আলাদা category হিসেবে রাখতে হবে।

## Important distinction

```text
Collapse:
probabilities প্রায় সমান

Reversal:
incorrect objective higher
```

একটি pair একই সঙ্গে reversed এবং near-zero হতে পারে:

```text
margin = -0.004
```

তাই report-এ category overlap পরিষ্কার করতে হবে।

---

# ১৪. Analysis Part E — Session-level discrimination metrics

Pair-level table-এর পাশাপাশি প্রতিটি mixed-label session-এর জন্য একটি summary row বানাব।

## Session positive mean probability

Session-এর correct objectives-এর average probability।

[
\bar p_{+}
==========

\text{mean probability of correct objectives}
]

---

## Session negative mean probability

Session-এর incorrect objectives-এর average probability।

[
\bar p_{-}
==========

\text{mean probability of incorrect objectives}
]

---

## Session margin

[
\text{session margin}
=====================

## \bar p_{+}

\bar p_{-}
]

### Example

```text
Correct objective probabilities:
0.80, 0.70

Mean positive = 0.75

Incorrect objective probabilities:
0.65, 0.60

Mean negative = 0.625

Session margin = 0.75 − 0.625 = 0.125
```

এখানে session-level discrimination ভালো।

---

## Session reversal

যদি:

```text
session margin < 0
```

তাহলে session average হিসেবে incorrect objectives বেশি probability পেয়েছে।

---

## Session probability spread

Session-এর সব objective prediction কতটা ছড়ানো, সেটি।

এটি standard deviation বা range দিয়ে দেখা যায়।

### Probability range

```text
maximum probability − minimum probability
```

উদাহরণ:

```text
0.74, 0.72, 0.70

Range = 0.74 − 0.70 = 0.04
```

সব objective প্রায় একই probability।

কিন্তু:

```text
0.85, 0.60, 0.30

Range = 0.55
```

Model objectives অনুযায়ী অনেক react করছে।

### Standard deviation

Standard deviation বলে values average-এর চারপাশে কতটা ছড়িয়েছে।

```text
Small standard deviation
→ সব objectives প্রায় একই probability

Large standard deviation
→ objectives অনুযায়ী prediction বদলাচ্ছে
```

কিন্তু standard deviation একা correctness বলে না।

Model ভুল direction-এও অনেক variation দিতে পারে। তাই এটি margin-এর সঙ্গে দেখতে হবে।

---

## Session Log Loss

একটি session-এর objectives-এর average Log Loss।

Log Loss probability confidence-এর ভুলকে measure করে।

### Incorrect objective-তে high probability

```text
Target = 0
Prediction = 0.90
```

খুব বড় penalty হবে।

### Correct objective-তে low probability

```text
Target = 1
Prediction = 0.10
```

এটিও বড় penalty।

Session Log Loss বলবে একটি session overall কত expensive।

---

# ১৫. Pair weighting বনাম session weighting

এটি খুব গুরুত্বপূর্ণ statistical issue।

ধরুন:

```text
Session A:
1 positive × 1 negative
= 1 pair

Session B:
5 positive × 5 negative
= 25 pairs
```

Pair-level average করলে Session B ফলাফলে ২৫ গুণ বেশি influence করবে।

এটি সবসময় desirable নয়।

## Pair-weighted result

প্রতিটি pair সমান weight পায়।

বড় session বেশি influence করে।

## Session-weighted result

প্রথমে প্রতিটি session-এর metric calculate হবে।

তারপর sessionগুলো equal weight পাবে।

```text
Session A weight = 1
Session B weight = 1
```

## আমাদের কী করা উচিত?

দুটিই report করব:

```text
Pair-weighted ranking accuracy
Session-weighted ranking accuracy
```

কিন্তু primary interpretation session-weighted result-এর দিকে বেশি থাকবে।

কারণ research unit মূলত tutoring session।

---

# ১৬. Analysis Part F — Collapse severity groups

প্রতিটি mixed-label session-কে simple group-এ ভাগ করা যায়।

## Strong discrimination

```text
session margin ≥ 0.10
```

Correct objectives পরিষ্কারভাবে higher।

## Weak positive discrimination

```text
0.02 ≤ session margin < 0.10
```

Direction correct, কিন্তু margin খুব বড় নয়।

## Collapse / near-equal

```text
|session margin| < 0.02
```

Positive ও negative objectives প্রায় একই probability।

## Reversed

```text
session margin ≤ -0.02
```

Incorrect objectives average হিসেবে বেশি probability পেয়েছে।

## কেন `0.02`?

এটি natural law নয়। এটি case classification-এর একটি operational threshold।

তাই robustness check হিসেবে:

```text
0.01
0.02
0.05
```

তিনটি threshold-এ result দেখব।

আগের analysis-এ threshold পরিবর্তন করলেও collapse burden stable ছিল। 

---

# ১৭. Analysis Part G — কোন ধরনের session-এ collapse বেশি?

Step 5-এ খুব বেশি subgroup analysis করব না; সেটি Step 6-এর কাজ।

শুধু same-session discrimination-এর সঙ্গে directly related structural factors দেখব।

## Factor 1 — Number of objectives

Groups:

```text
2 objectives
3–4 objectives
5+ objectives
```

Question:

> Objective সংখ্যা বাড়লে margin কমছে কি?

---

## Factor 2 — Transcript length

Transcript length word count বা character count দিয়ে নেওয়া যায়।

Groups:

```text
Short
Medium
Long
Very long
```

Question:

> Long transcript-এর lexical mass objective signal চাপা দিচ্ছে কি?

এটি hypothesis, final conclusion নয়।

---

## Factor 3 — Student/tutor text balance

সহজ ratio:

[
\text{student share}
====================

\frac{\text{student word count}}
{\text{student word count}+\text{tutor word count}}
]

### Student-dominant

Student words বেশি।

### Tutor-dominant

Tutor words বেশি।

### Balanced

দুই speaker-এর participation কাছাকাছি।

Question:

> Tutor-dominant sessions-এ objective margin কম কি না?

আগের analysis tutor intervention student mastery-এর clean evidence নয় বলে দেখিয়েছে। 

---

## Factor 4 — Number of positive and negative objectives

উদাহরণ:

```text
1 positive, 1 negative
1 positive, many negatives
many positives, 1 negative
many positives, many negatives
```

Question:

> Imbalanced objective composition model-এর ranking result বদলায় কি?

---

## Factor 5 — Session mean confidence

Session-এর সব probability-এর average।

```text
High session confidence
→ model পুরো session-কে generally correct মনে করছে

Low session confidence
→ model পুরো session-কে generally incorrect মনে করছে
```

Question:

> High-confidence mixed session-এ negative objectives false positive হচ্ছে কি?

এটি current positive-biased model-এর জন্য গুরুত্বপূর্ণ।

---

# ১৮. Analysis Part H — Reversed pair analysis

Reversal collapse-এর চেয়ে বেশি serious।

## Reversed pair

```text
p_positive < p_negative
```

## আমরা বের করব

```text
Total reversed pairs
Reversal rate
Mean reversed margin
Median reversed margin
Most severe reversed pairs
High-confidence reversed negatives
```

## Severe reversal example

```text
Correct objective   → 0.40
Incorrect objective → 0.88

Margin = -0.48
```

এ ধরনের case future manual review-এর top priority।

## কেন?

এটি শুধু insufficient separation নয়।

এখানে model objective-specific signal ভুল direction-এ ব্যবহার করছে।

---

# ১৯. Analysis Part I — Error case extraction

Step 5-এর শেষে শুধু summary table রাখলে চলবে না। Actual cases save করতে হবে।

## Case group 1 — Severe collapse

```text
|margin| < 0.01
```

## Case group 2 — Severe reversal

সবচেয়ে negative margin।

## Case group 3 — Successful discrimination

সবচেয়ে বড় positive margin।

এগুলো বোঝাবে model কখন ঠিক কাজ করে।

## Case group 4 — High-confidence false positives

```text
Negative objective probability ≥ 0.80
```

## Case group 5 — Many-objective sessions

অনেক objective এবং low margin।

## Case group 6 — High-loss sessions

সবচেয়ে বেশি session Log Loss।

---

# ২০. প্রতিটি case file-এ কী থাকবে?

```text
session_id
fold
full transcript
student text
tutor text
positive objective
negative objective
positive probability
negative probability
margin
positive target
negative target
session objective count
session log loss
collapse group
```

এই information Step 8 manual review-এর input হবে।

অর্থাৎ Step 5 শুধু numerical result তৈরি করবে না; পরবর্তী human review-এর sample foundation তৈরি করবে।

---

# ২১. প্রয়োজনীয় plots

অনেক plot বানাব না। চারটি main plot যথেষ্ট।

## Plot 1 — Positive বনাম negative probability scatter plot

X-axis:

```text
Incorrect objective probability
```

Y-axis:

```text
Correct objective probability
```

Diagonal line:

```text
y = x
```

### Interpretation

Diagonal-এর ওপরে:

```text
Correct objective probability higher
```

Diagonal-এর নিচে:

```text
Incorrect objective probability higher
```

Diagonal-এর খুব কাছে:

```text
Collapse বা weak separation
```

---

## Plot 2 — Pairwise margin distribution

X-axis:

```text
Probability margin
```

Y-axis:

```text
Number/density of pairs
```

Vertical line:

```text
margin = 0
```

### Interpretation

* Right side → correct ordering
* Near zero → collapse
* Left side → reversal

এটি Step 5-এর সবচেয়ে important plot।

---

## Plot 3 — Session margin by objective count

X-axis:

```text
2 objectives
3–4 objectives
5+ objectives
```

Y-axis:

```text
Session margin
```

### Interpretation

Objective সংখ্যা বাড়ার সঙ্গে margin কমলে complexity hypothesis support পাবে।

---

## Plot 4 — Collapse category summary

Bar chart:

```text
Strong discrimination
Weak discrimination
Collapse
Reversed
```

প্রতিটি category-তে:

```text
Session count
Session share
Mean session loss
```

দেখানো যেতে পারে।

---

# ২২. Optional plot

Code এবং result পরিষ্কার থাকলে একটি heatmap করা যায়:

```text
Transcript-length group
×
Objective-count group
→ Mean session margin
```

তবে এটি optional।

প্রথম run-এ প্রয়োজন নেই।

---

# ২৩. Step 5-এর final output files

নতুন root অনুযায়ী:

```text
baselineanalysis_2/
└── 05_session_objective/
    ├── population_summary.csv
    ├── session_objective_metrics.csv
    ├── objective_pairs.parquet
    ├── collapse_summary.csv
    ├── collapse_cases.parquet
    ├── reversed_cases.parquet
    ├── successful_cases.parquet
    └── figures/
        ├── positive_vs_negative_probability.png
        ├── pair_margin_distribution.png
        ├── margin_by_objective_count.png
        └── collapse_category_summary.png
```

সব output save করতেই হবে এমন নয়।

Minimum useful files:

```text
session_objective_metrics.csv
objective_pairs.parquet
collapse_cases.parquet
figures/
```

পুরোনো plan-এ Step 5-এর জন্য session performance, objective performance, mixed-label sessions এবং collapse cases রাখার কথা ছিল। 

---

# ২৪. Notebook-এর Step 5 cell structure

Step 5-কে ৩০–৪০টি cell-এ ভাগ করব না।

## Cell 1 — Step title and research questions

Markdown cell।

এখানে থাকবে:

```text
Objective
Research questions
Hypotheses
Primary population
Main metrics
```

---

## Cell 2 — Load OOF and metadata

শুধু required files load ও merge।

---

## Cell 3 — Integrity check

Required columns, missing values, duplicates, probability range।

---

## Cell 4 — Build session summary

প্রতি session:

```text
n_objectives
n_positive
n_negative
session type
```

---

## Cell 5 — Select mixed-label sessions

Primary Step 5 population তৈরি।

---

## Cell 6 — Build positive-negative pair table

প্রতিটি positive objective বনাম প্রতিটি negative objective।

---

## Cell 7 — Calculate pair metrics

```text
margin
ranking_correct
reversed
severe_collapse
pair loss
```

---

## Cell 8 — Calculate session metrics

```text
positive mean
negative mean
session margin
probability spread
session loss
```

---

## Cell 9 — Main scorecard

একটি clean table:

```text
Mixed sessions
Pairwise accuracy
Session-weighted accuracy
Mean margin
Median margin
Collapse rate
Reversal rate
Mixed-session Log Loss
```

---

## Cell 10 — Main plots

চারটি useful plot।

---

## Cell 11 — Structural comparison

Objective count, transcript length এবং student/tutor balance অনুযায়ী margin।

---

## Cell 12 — Case extraction

Collapse, reversal এবং successful cases save।

---

## Cell 13 — Research interpretation

Markdown conclusion।

সুতরাং পুরো Step 5 প্রায়:

```text
13 clean cells
```

এর মধ্যে কয়েকটি markdown। Giant code প্রয়োজন নেই।

---

# ২৫. Primary Step 5 scorecard

শেষে একটি table থাকবে:

| Metric                        | Meaning                                    |
| ----------------------------- | ------------------------------------------ |
| Mixed-label sessions          | কত session-এ actual discrimination প্রয়োজন |
| Mixed-session responses       | ঐ sessions-এ মোট response                  |
| Positive-negative pairs       | কত objective pair compare হয়েছে            |
| Pair-weighted accuracy        | সব pair-এর মধ্যে correct ordering          |
| Session-weighted accuracy     | সব session-কে সমান weight দিয়ে ordering    |
| Mean margin                   | average separation                         |
| Median margin                 | typical separation                         |
| Severe-collapse share         | প্রায় একই probability পাওয়া pair           |
| Reversal rate                 | incorrect objective higher হওয়া pair       |
| Mixed-session Log Loss        | difficult sessions-এর probability quality  |
| High-confidence negative rate | incorrect objective-তে high probability    |

---

# ২৬. Result কীভাবে interpret করব?

## Scenario A

```text
Pairwise accuracy high
Margin high
Reversal low
```

অর্থ:

> Model objective-specific discrimination ভালো করছে।

এটি বর্তমান evidence অনুযায়ী unlikely।

---

## Scenario B

```text
Pairwise accuracy moderately high
Margin near zero
```

অর্থ:

> Model direction কিছুটা বুঝছে, কিন্তু signal compressed।

এটাই এখনকার expected result।

---

## Scenario C

```text
Pairwise accuracy near 50%
Margin near zero
```

অর্থ:

> Model objective-level distinction প্রায় random।

---

## Scenario D

```text
Pairwise accuracy below 50%
Negative mean margin
```

অর্থ:

> Model systematicভাবে incorrect objectives-কে বেশি score করছে।

---

## Scenario E

```text
Overall result moderate
কিন্তু 5+ objective session-এ খুব খারাপ
```

অর্থ:

> Session complexity objective discrimination failure-এর গুরুত্বপূর্ণ factor।

---

## Scenario F

```text
Tutor-heavy session-এ margin low
```

অর্থ:

> Tutor intervention/shared transcript language objective-specific student evidence চাপা দিতে পারে।

তবে এটি association, causal proof নয়।

---

# ২৭. কোন conclusion লেখা যাবে এবং কোনটি যাবে না

## লেখা যাবে

```text
Mixed-label sessions-এ margin ছোট।
Objective count বাড়লে margin কমেছে।
Tutor-heavy group-এ collapse rate বেশি।
Incorrect objectives high probability পেয়েছে।
```

যদি result সত্যিই এগুলো support করে।

## লেখা যাবে না

```text
Tutor text collapse ঘটিয়েছে।
Long transcript objective signal destroy করে।
Student text useless।
Specific model architecture নিশ্চিতভাবে improve করবে।
```

কারণ Step 5 observational analysis।

এটি relationship দেখাবে, cause প্রমাণ করবে না।

Cause সম্পর্কে stronger evidence Step 9 counterfactual এবং Step 10 ablation থেকে আসবে।

---

# ২৮. Step 5-এ কী করা হবে না

Step 5-কে ছোট ও focused রাখতে এগুলো করব না:

* নতুন model train করব না;
* SHAP পুনরায় calculate করব না;
* calibration করব না;
* সব possible metadata group analyse করব না;
* transformer ব্যবহার করব না;
* feature delete করব না;
* oracle probability correction করব না;
* objective prior model বানাব না;
* manual transcript annotation এখনই করব না।

এগুলো পরের steps-এর কাজ।

---

# ২৯. Step 5-এর success criteria

Step 5 successful হবে যখন আমরা নির্ভরযোগ্যভাবে বলতে পারব:

1. Same-session discrimination-এর usable population কত বড়।
2. Model correct এবং incorrect objective কী হারে সঠিকভাবে rank করে।
3. Typical probability margin কত।
4. Collapse কতটা common।
5. Reversal কতটা common।
6. Collapse কোন structural session type-এ বেশি।
7. কোন cases manual review-এর জন্য নিতে হবে।
8. V2 model-এর কোন requirement সবচেয়ে বেশি justified।

---

# ৩০. Expected final research conclusion-এর template

Result পাওয়ার আগে exact numbers লিখব না। কিন্তু final conclusion-এর structure হবে:

> Mixed-label sessions baseline-এর জন্য একটি high-risk evaluation slice। Model correct objectives-কে incorrect objectives-এর তুলনায় [X%] pair-এ higher probability দিয়েছে, তবে median probability margin ছিল মাত্র [Y], যা objective-specific signal compression নির্দেশ করে। [Z%] pairs severe collapse threshold-এর মধ্যে এবং [R%] pairs reversed ছিল। Collapse বিশেষভাবে [session type]-এ concentrated ছিল। এই ফলাফল দেখায় যে current word-level TF-IDF model transcript-এর session-wide impression ব্যবহার করলেও objective অনুযায়ী student evidence যথেষ্টভাবে পৃথক করতে পারে না। তাই V2 model-এ objective-conditioned evidence extraction, speaker separation এবং within-session ranking support প্রয়োজন।

---

# Step 5-এর সবচেয়ে সহজ সারাংশ

```text
প্রথমে mixed-label sessions খুঁজব
        ↓
Correct এবং incorrect objectives pair করব
        ↓
দুইটির probability compare করব
        ↓
Margin, ranking, collapse ও reversal হিসাব করব
        ↓
Session-wise summary তৈরি করব
        ↓
কোন ধরনের session-এ failure বেশি দেখব
        ↓
Important real cases save করব
        ↓
V2 architecture-এর evidence তৈরি করব
```

## Step 5-এর central idea

> **একই transcript-এর মধ্যে model objective বদলালে judgement বদলাচ্ছে কি না—এবং না বদলালে ঠিক কোন পরিস্থিতিতে না বদলাচ্ছে—সেটিই Step 5-এর সম্পূর্ণ গবেষণা।**

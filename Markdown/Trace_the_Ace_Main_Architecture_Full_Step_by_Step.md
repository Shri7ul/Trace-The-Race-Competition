# Trace the Ace — Main Architecture
## Full Step-by-Step Explanation with One Running Example, Outputs, and Formulas

---

## 1. Main Goal

আমাদের পুরো architecture-এর মূল উদ্দেশ্য হলো:

$$
\boxed{
\text{Session Transcript}
+
\text{Learning Objective}
\rightarrow
P(\text{Student will answer correctly})
}
$$

অর্থাৎ model শুধু পুরো transcript দেখে student সম্পর্কে একটি general impression তৈরি করবে না।

বরং model-এর প্রশ্ন হবে:

> **এই specific session-এ, এই specific learning objective-এর জন্য student আসলে কতটা mastery দেখিয়েছে?**

এই distinction-টাই architecture-এর কেন্দ্রীয় idea।

---

## 2. Full Architecture at a Glance

```text
RAW ORDERED TRANSCRIPT
        ↓
CANONICAL TURN RECONSTRUCTION
(role + timestamp + true order)
        ↓
LEARNING OBJECTIVE
        ↓
SPARSE RETRIEVAL + DENSE RETRIEVAL
(TF-IDF + char/math overlap + Sentence-Transformer)
        ↓
CANDIDATE UNION
        ↓
CROSS-ENCODER RERANKING
        ↓
OBJECTIVE-SPECIFIC TURNS
        ↓
ROLE + TIME EVIDENCE PACK
        ↓
MODERNBERT-BASE
(max_length = 2048)
        ↓
SEMANTIC MASTERY LOGIT
z_sem
        ↓
BCE LOSS + SAME-SESSION PAIRWISE LOSS
        ↓
PARALLEL STRUCTURED FEATURE BRANCH
        ↓
EVIDENCE-CONFIDENCE GATE
        ↓
FOLD-SAFE OBJECTIVE PRIOR
        ↓
SIMPLE FUSION
        ↓
NEURAL PROBABILITY
        ↓
+ TF-IDF LOGISTIC MODEL
        ↓
OOF BLEND
        ↓
OPTIONAL CALIBRATION
        ↓
FINAL PROBABILITY
```

---

## 3. Running Example

পুরো architecture বোঝানোর জন্য একই example শুরু থেকে শেষ পর্যন্ত ব্যবহার করা হবে।

### Session

```text
Session ID = S101

10:01 Tutor:
Which is larger, 1/3 or 1/4?

10:02 Student:
I think 1/4.

10:03 Tutor:
Think about the size of each piece.

10:04 Student:
Oh, 1/3 is larger.

10:05 Student:
Because thirds are bigger pieces than fourths.

10:06 Tutor:
Good.

10:10 Tutor:
Now add 1/3 and 1/4.

10:11 Student:
I don't know.
```

এই একই session-এর দুইটি learning objective আছে:

```text
Objective A:
Compare fractions with different denominators

Objective B:
Add fractions with different denominators
```

Actual labels:

```text
Objective A → label = 1
Objective B → label = 0
```

---

# STEP 1 — Raw Ordered Transcript

প্রথম input হলো original ordered tutoring conversation।

এখানে preserve করতে হবে:

- কে কথা বলেছে
- কী বলেছে
- কখন বলেছে
- কোন utterance-এর পরে কোন utterance এসেছে

এই raw transcript-ই পরের সব analysis-এর source।

---

# STEP 2 — Canonical Turn Reconstruction

Raw transcript থেকে একটি trusted turn-level table তৈরি হবে।

| session_id | turn_id | role | order | timestamp | text |
|---|---:|---|---:|---|---|
| S101 | U1 | Tutor | 1 | 10:01 | Which is larger, 1/3 or 1/4? |
| S101 | U2 | Student | 2 | 10:02 | I think 1/4. |
| S101 | U3 | Tutor | 3 | 10:03 | Think about the size of each piece. |
| S101 | U4 | Student | 4 | 10:04 | Oh, 1/3 is larger. |
| S101 | U5 | Student | 5 | 10:05 | Because thirds are bigger pieces than fourths. |
| S101 | U6 | Tutor | 6 | 10:06 | Good. |
| S101 | U7 | Tutor | 7 | 10:10 | Now add 1/3 and 1/4. |
| S101 | U8 | Student | 8 | 10:11 | I don't know. |

মূল information:

$$
\boxed{\text{Role + Timestamp + True Order}}
$$

Chronology:

```text
Student wrong attempt
        ↓
Tutor hint
        ↓
Student correction
        ↓
Student explanation
```

---

# STEP 3 — Learning Objective Conditioning

ধরি:

$$
O_A =
\text{Compare fractions with different denominators}
$$

এই objective session-এর প্রতিটি turn-এর সঙ্গে compare হবে:

$$
O_A \times U_1
$$

$$
O_A \times U_2
$$

$$
\cdots
$$

$$
O_A \times U_8
$$

মূল প্রশ্ন:

> **এই objective বোঝার জন্য কোন turnগুলো relevant?**

---

# STEP 4 — Sparse Retrieval

Sparse retrieval exact lexical, character এবং mathematical overlap ধরবে।

$$
\boxed{
S_{\text{sparse}}
=
\alpha S_{\text{TFIDF}}
+
\beta S_{\text{char}}
+
\gamma S_{\text{math}}
}
$$

যেখানে:

- $S_{\text{TFIDF}}$ = word/phrase similarity
- $S_{\text{char}}$ = character-level similarity
- $S_{\text{math}}$ = mathematical token overlap

### TF-IDF Similarity

$$
\boxed{
S_{\text{TFIDF}}(O,T_i)
=
\frac{
\vec{O}\cdot\vec{T_i}
}{
\|\vec{O}\|\,\|\vec{T_i}\|
}
}
$$

Example:

| Turn | Text | Sparse Score |
|---|---|---:|
| U1 | Which is larger, 1/3 or 1/4? | 0.83 |
| U2 | I think 1/4. | 0.36 |
| U3 | Think about the size of each piece. | 0.19 |
| U4 | 1/3 is larger. | 0.63 |
| U5 | Thirds are bigger pieces than fourths. | 0.48 |
| U7 | Add 1/3 and 1/4. | 0.60 |

U7-এর score তুলনামূলক বেশি কারণ `1/3` এবং `1/4` exact mathematical tokens match করছে। কিন্তু U7 comparison নয়, addition-এর কথা বলছে। এটাই sparse retrieval-এর limitation।

---

# STEP 5 — Dense Retrieval

Sentence-Transformer semantic meaning ধরবে।

$$
e_O = f_{\text{ST}}(O)
$$

$$
e_{T_i} = f_{\text{ST}}(T_i)
$$

$$
\boxed{
S_{\text{dense}}(O,T_i)
=
\cos(e_O,e_{T_i})
}
$$

Example:

| Turn | Dense Score |
|---|---:|
| U1 | 0.91 |
| U2 | 0.66 |
| U3 | 0.78 |
| U4 | 0.90 |
| U5 | 0.95 |
| U7 | 0.46 |

`Because thirds are bigger pieces than fourths.` exact `compare fractions` না বললেও meaning strongly related, তাই dense score বেশি।

---

# STEP 6 — Candidate Union

Sparse top turns:

```text
U1, U4, U7, U5
```

Dense top turns:

```text
U5, U1, U4, U3, U2
```

Union:

$$
\boxed{
C
=
C_{\text{sparse}}
\cup
C_{\text{dense}}
}
$$

Final candidate pool:

```text
U1, U2, U3, U4, U5, U7
```

---

# STEP 7 — Cross-Encoder Reranking

Cross-Encoder objective এবং candidate turn একসাথে পড়ে relevance judge করবে।

$$
\boxed{
r_i
=
f_{\text{CE}}(O,T_i)
}
$$

Example:

| Rank | Turn | Role | Cross-Encoder Score |
|---:|---|---|---:|
| 1 | U5 | Student | 0.97 |
| 2 | U4 | Student | 0.94 |
| 3 | U1 | Tutor | 0.92 |
| 4 | U3 | Tutor | 0.83 |
| 5 | U2 | Student | 0.72 |
| 6 | U7 | Tutor | 0.21 |

Sparse-এ U7 ছিল 0.60, Cross-Encoder-এর পরে 0.21 — কারণ এটা fraction-related হলেও comparison objective-এর evidence নয়।

---

# STEP 8 — Objective-Specific Turns

Relevant turns:

```text
U1 Tutor   → objective-specific question
U2 Student → wrong initial attempt
U3 Tutor   → scaffold/hint
U4 Student → corrected answer
U5 Student → explanation
```

এখন আমাদের কাছে:

$$
\boxed{\text{Objective-Specific Evidence}}
$$

---

# STEP 9 — Role + Time Evidence Pack

```text
[OBJECTIVE]
Compare fractions with different denominators

[STUDENT_BEFORE_FEEDBACK]
I think 1/4.

[TUTOR_CONTEXT]
Which is larger, 1/3 or 1/4?
Think about the size of each piece.

[STUDENT_AFTER_FEEDBACK]
Oh, 1/3 is larger.
Because thirds are bigger pieces than fourths.

[FINAL_STUDENT_EVIDENCE]
Because thirds are bigger pieces than fourths.

[NEGATIVE_OR_UNCERTAIN_EVIDENCE]
I think 1/4.
```

এই stage শেষে main row-wise dataset তৈরি হয়।

| response_id | session_id | objective | student_before | tutor_context | student_after | final_student | negative_evidence | label |
|---|---|---|---|---|---|---|---|---:|
| R1 | S101 | Compare fractions... | I think 1/4. | Think about size... | 1/3 is larger... | Thirds are bigger... | I think 1/4. | 1 |

$$
\boxed{
1\text{ row}
=
1\text{ session-objective response}
}
$$

---

# STEP 10 — Tokenization

Evidence pack ModernBERT tokenizer-এ যাবে।

যদি:

$$
N_{\text{tokens}}=620
$$

তাহলে সব evidence থাকবে।

যদি:

$$
N_{\text{tokens}}=2500
$$

তাহলে priority-based truncation:

```text
1. Objective
2. Strong student evidence
3. Final student evidence
4. Student pre/post feedback sequence
5. Tutor context
6. Weak/duplicate evidence
```

Final condition:

$$
\boxed{
N_{\text{tokens}}\le2048
}
$$

---

# STEP 11 — ModernBERT-base

$$
\boxed{
h_i
=
\text{ModernBERT}(x_i)
}
$$

Conceptual representation:

$$
h_i=[0.21,-0.45,0.78,\ldots]
$$

এটা probability নয়; এটা contextual representation।

---

# STEP 12 — Semantic Mastery Logit

$$
\boxed{
z_{\text{sem}}
=
w^\top h_i+b
}
$$

ধরি:

$$
z_{\text{sem}}=1.35
$$

Sigmoid:

$$
\sigma(z)=\frac{1}{1+e^{-z}}
$$

$$
p_{\text{sem}}
=
\sigma(1.35)
\approx0.794
$$

অর্থাৎ:

$$
\boxed{
P(\text{correct})\approx79.4\%
}
$$

এটা এখনো final probability নয়।

---

# STEP 13 — BCE Loss

$$
\boxed{
L_{\text{BCE}}
=
-
\left[
y\log(p)
+
(1-y)\log(1-p)
\right]
}
$$

যদি:

$$
y=1,\quad p=0.794
$$

তাহলে:

$$
L_{\text{BCE}}
=
-\log(0.794)
\approx0.231
$$

BCE individual response correctness শেখায়।

---

# STEP 14 — Same-Session Pairwise Loss

Same session-এর Objective B-এর logit ধরি:

$$
z^-=-0.60
$$

Correct Objective A:

$$
z^+=1.35
$$

আমরা চাই:

$$
\boxed{
z^+>z^-
}
$$

Pairwise loss:

$$
\boxed{
L_{\text{pair}}
=
\log
\left(
1+e^{-(z^+-z^-)}
\right)
}
$$

যদি wrong objective-এর logit correct objective-এর চেয়ে বড় হয়, loss বড় হবে।

---

# STEP 15 — Total Training Loss

$$
\boxed{
L
=
L_{\text{BCE}}
+
\lambda_{\text{pair}}L_{\text{pair}}
}
$$

Example:

$$
L_{\text{BCE}}=0.30
$$

$$
L_{\text{pair}}=0.50
$$

$$
\lambda_{\text{pair}}=0.10
$$

তাহলে:

$$
L=0.30+0.10(0.50)
$$

$$
\boxed{
L=0.35
}
$$

```text
TOTAL LOSS
    ↓
Backpropagation
    ↓
ModernBERT weights update
```

---

# STEP 16 — Parallel Structured Feature Branch

তিনটি feature family:

```text
A. Retrieval / Confidence
B. Tutor / Help
C. Temporal / Negative
```

### Retrieval / Confidence

```text
student_support_max       = 0.96
student_support_topk_mean = 0.84
retrieval_margin          = 0.32
evidence_coverage         = 0.88
cross_encoder_top1        = 0.97
```

### Tutor / Help

```text
tutor_support_max      = 0.81
student_support_max    = 0.96
tutor_minus_student    = -0.15
post_feedback_gain     = +0.35
tutor_correction_count = 1
```

### Temporal / Negative

```text
pre_feedback_support  = 0.30
post_feedback_support = 0.86
final_segment_support = 0.92
uncertainty_score     = 0.20
answer_change         = 1
```

---

# STEP 17 — 20–35 Structured Features

$$
\boxed{
x_{\text{struct}}
=
[x_1,x_2,\ldots,x_d]
}
$$

যেখানে:

$$
d\approx20\text{–}35
$$

Conceptually:

$$
\boxed{
\text{ModernBERT}=\text{semantic meaning}
}
$$

$$
\boxed{
\text{Structured Features}=\text{evidence behaviour + confidence}
}
$$

---

# STEP 18 — Evidence-Confidence Gate

$$
\boxed{
g
=
\sigma
\left(
w_g^\top x_{\text{confidence}}+b_g
\right)
}
$$

যেখানে:

$$
0\le g\le1
$$

Strong evidence:

$$
g\rightarrow1
$$

Weak evidence:

$$
g\rightarrow0
$$

Example:

$$
g=0.90
$$

$$
g z_{\text{sem}}
=
0.90\times1.35
=
\boxed{1.215}
$$

---

# STEP 19 — Fold-Safe Objective Prior

ধরি training fold-এ একটি objective-এর:

```text
Number of samples = 100
Positive samples  = 75
```

Global positive rate:

$$
p_{\text{global}}=0.70
$$

Smoothed prior:

$$
\boxed{
p_o
=
\frac{
n_o^+
+
\alpha p_{\text{global}}
}{
n_o+\alpha
}
}
$$

যদি:

$$
\alpha=20
$$

তাহলে:

$$
p_o
=
\frac{75+20(0.70)}{100+20}
=
\frac{89}{120}
\approx0.742
$$

Prior logit:

$$
\boxed{
z_{\text{prior}}
=
\log
\left(
\frac{p_o}{1-p_o}
\right)
}
$$

Example:

$$
z_{\text{prior}}\approx1.06
$$

Validation row-এর own label prior তৈরিতে ব্যবহার হবে না; তাই prior **fold-safe**।

---

# STEP 20 — Simple Fusion

Available signals:

```text
Semantic logit        = 1.35
Evidence gate         = 0.90
Objective prior logit = 1.06
Structured features   = 20–35 values
```

Fusion:

$$
\boxed{
z_{\text{fusion}}
=
\beta_0
+
\beta_1 z_{\text{prior}}
+
\beta_2(g z_{\text{sem}})
+
\beta^\top x_{\text{struct}}
}
$$

ধরি:

$$
z_{\text{fusion}}=1.50
$$

---

# STEP 21 — Neural Probability

$$
\boxed{
p_{\text{neural}}
=
\sigma(z_{\text{fusion}})
}
$$

$$
p_{\text{neural}}
=
\sigma(1.50)
\approx
\boxed{0.818}
$$

---

# STEP 22 — Separate TF-IDF Logistic Model

Parallel branch:

```text
Objective + Text
      ↓
TF-IDF
      ↓
Logistic Regression
      ↓
Probability
```

Formula:

$$
\boxed{
p_{\text{TFIDF}}
=
\sigma
\left(
w_T^\top x_{\text{TFIDF}}+b_T
\right)
}
$$

ধরি:

$$
p_{\text{TFIDF}}=0.71
$$

তাহলে:

```text
Neural = 0.818
TF-IDF = 0.710
```

---

# STEP 23 — OOF Predictions

5-fold session-grouped validation-এ:

| response_id | label | neural_OOF | tfidf_OOF |
|---|---:|---:|---:|
| R1 | 1 | 0.818 | 0.710 |
| R2 | 0 | 0.310 | 0.460 |
| R3 | 1 | 0.770 | 0.730 |
| R4 | 0 | 0.440 | 0.500 |

প্রতিটি OOF prediction এমন model থেকে আসবে যেটা ওই session training-এ দেখেনি।

---

# STEP 24 — OOF Blend

$$
\boxed{
p_{\text{blend}}
=
w p_{\text{neural}}
+
(1-w)p_{\text{TFIDF}}
}
$$

OOF Log Loss minimize করে best $w$ select হবে।

যদি:

$$
w=0.80
$$

তাহলে:

$$
p_{\text{blend}}
=
0.80(0.818)+0.20(0.710)
$$

$$
=
0.6544+0.142
$$

$$
\boxed{
p_{\text{blend}}=0.7964
}
$$

---

# STEP 25 — Optional Calibration

Calibration mandatory নয়।

### Temperature Scaling

$$
z
=
\log
\left(
\frac{p}{1-p}
\right)
$$

$$
\boxed{
p_{\text{cal}}
=
\sigma
\left(
\frac{z}{T}
\right)
}
$$

### Platt Scaling

$$
\boxed{
p_{\text{cal}}
=
\sigma(az+b)
}
$$

Calibration keep করব only if:

$$
LL_{\text{calibrated}}
<
LL_{\text{uncalibrated}}
$$

না হলে uncalibrated blend-ই final থাকবে।

---

# STEP 26 — Final Probability

ধরি:

$$
p_{\text{blend}}=0.796
$$

Calibration শেষে:

$$
p_{\text{final}}=0.780
$$

Final submission:

| response_id | final_probability |
|---|---:|
| R1 | **0.780** |

অর্থাৎ:

$$
\boxed{
P(y=1\mid S101,O_A)=0.780
}
$$

---

# STEP 27 — Same Session, Different Objective

Objective B:

```text
Add fractions with different denominators
```

Evidence:

```text
Student:
I don't know.
```

Possible signals:

```text
Student support     = low
Uncertainty         = high
Final support       = low
Tutor dominance     = high
Evidence confidence = weak
```

ধরি:

$$
z_{\text{sem}}=-0.75
$$

$$
g=0.35
$$

$$
p_o=0.68
$$

Fusion শেষে:

$$
p_{\text{neural}}=0.36
$$

TF-IDF:

$$
p_{\text{TFIDF}}=0.50
$$

Blend:

$$
p_{\text{blend}}=0.39
$$

Final:

$$
\boxed{
p_{\text{final}}\approx0.40
}
$$

একই session-এর দুই objective:

| Objective | Final Probability |
|---|---:|
| Compare fractions | **0.78** |
| Add fractions | **0.40** |

এটাই architecture-এর core success condition।

---

# 28. Full System — Mathematical Summary

ধরি:

$$
S=\text{Session}
$$

$$
O=\text{Learning Objective}
$$

### Hybrid Retrieval

$$
\boxed{
C
=
TopK_{\text{sparse}}(S,O)
\cup
TopK_{\text{dense}}(S,O)
}
$$

### Cross-Encoder

$$
\boxed{
E
=
TopK
\left(
f_{\text{CE}}(O,C)
\right)
}
$$

### Evidence Pack

$$
\boxed{
X
=
Pack(E,\text{role},\text{time})
}
$$

### ModernBERT

$$
\boxed{
h
=
ModernBERT(X)
}
$$

### Semantic Logit

$$
\boxed{
z_{\text{sem}}
=
w^\top h+b
}
$$

### BCE

$$
\boxed{
L_{\text{BCE}}
=
-
\left[
y\log(p)
+
(1-y)\log(1-p)
\right]
}
$$

### Pairwise Loss

$$
\boxed{
L_{\text{pair}}
=
\log
\left(
1+e^{-(z^+-z^-)}
\right)
}
$$

### Total Loss

$$
\boxed{
L
=
L_{\text{BCE}}
+
\lambda_{\text{pair}}L_{\text{pair}}
}
$$

### Structured Features

$$
\boxed{
x_{\text{struct}}
=
f_{\text{features}}(E)
}
$$

### Confidence Gate

$$
\boxed{
g
=
\sigma
\left(
w_g^\top x_{\text{confidence}}+b_g
\right)
}
$$

### Objective Prior

$$
\boxed{
p_o
=
\frac{
n_o^+
+
\alpha p_{\text{global}}
}{
n_o+\alpha
}
}
$$

$$
\boxed{
z_{\text{prior}}
=
\log
\left(
\frac{p_o}{1-p_o}
\right)
}
$$

### Fusion

$$
\boxed{
z_{\text{fusion}}
=
\beta_0
+
\beta_1 z_{\text{prior}}
+
\beta_2 g z_{\text{sem}}
+
\beta^\top x_{\text{struct}}
}
$$

### Neural Probability

$$
\boxed{
p_N
=
\sigma(z_{\text{fusion}})
}
$$

### TF-IDF Probability

$$
\boxed{
p_T
=
\sigma
\left(
w_T^\top x_{\text{TFIDF}}+b_T
\right)
}
$$

### OOF Blend

$$
\boxed{
p_B
=
w p_N
+
(1-w)p_T
}
$$

### Optional Calibration

$$
\boxed{
p_{\text{final}}
=
Calibrate(p_B)
}
$$

### Final Prediction

$$
\boxed{
P(y=1\mid S,O)
=
p_{\text{final}}
}
$$

---

# 29. Architecture as Five Intelligence Layers

## Layer A — Find the Right Evidence

```text
Sparse Retrieval
      +
Dense Retrieval
      +
Cross-Encoder
```

Question:

> **Objective-এর জন্য relevant conversation কোথায়?**

## Layer B — Understand Evidence Structure

```text
Role
+
Time
+
Before/After Feedback
+
Tutor/Student Separation
```

Question:

> **Evidence কে দিয়েছে, কখন দিয়েছে, এবং কোন sequence-এ এসেছে?**

## Layer C — Understand Semantic Mastery

```text
ModernBERT
+
BCE
+
Same-Session Pairwise Learning
```

Question:

> **Student-এর actual mastery evidence কী বলছে?**

## Layer D — Correct for Evidence Quality and Context

```text
Structured Features
+
Evidence-Confidence Gate
+
Fold-Safe Objective Prior
```

Question:

> **Semantic evidence কতটা trustworthy, tutor assistance কতটা, এবং objective historically কতটা easy/hard?**

## Layer E — Produce the Final Robust Probability

```text
Neural Model
+
TF-IDF Logistic
+
OOF Blend
+
Optional Calibration
```

Question:

> **সব complementary signal combine করলে safest final probability কত?**

---

# 30. Core Architectural Philosophy

Old-style approach:

$$
\boxed{
\text{Whole Transcript}
\rightarrow
\text{Prediction}
}
$$

আমাদের approach:

$$
\boxed{
\text{Transcript}
\rightarrow
\text{Objective-Specific Evidence}
\rightarrow
\text{Student Behaviour}
\rightarrow
\text{Semantic Mastery}
\rightarrow
\text{Evidence Confidence}
\rightarrow
\text{Final Probability}
}
$$

Central principle:

$$
\boxed{
\text{Objective-Specific Evidence}
>
\text{General Session Impression}
}
$$

---

# 31. End-to-End Data Transformation

```text
RAW UTTERANCE DATA
1 row = 1 utterance
        ↓
CANONICAL TURN TABLE
1 row = 1 trusted ordered turn
        ↓
OBJECTIVE × TURN TABLE
1 row = 1 objective-turn relationship
        ↓
RANKED OBJECTIVE-SPECIFIC TURNS
        ↓
ROLE + TIME EVIDENCE PACK
1 row = 1 session-objective response
        ↓
MODERNBERT + STRUCTURED FEATURES
        ↓
NEURAL OOF PREDICTION
        +
TF-IDF OOF PREDICTION
        ↓
OOF BLEND
        ↓
OPTIONAL CALIBRATION
        ↓
FINAL TEST PROBABILITY
```

---

# 32. Final One-Line Summary

$$
\boxed{
\text{Find the right evidence}
\rightarrow
\text{understand who said what and when}
\rightarrow
\text{estimate semantic mastery}
\rightarrow
\text{correct using evidence quality and objective difficulty}
\rightarrow
\text{blend complementary models}
\rightarrow
\text{output final probability}
}
$$

এটাই **Trace the Ace — Main Architecture**-এর complete step-by-step formulation.

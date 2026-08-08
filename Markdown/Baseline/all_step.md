হ্যাঁ ভাই। এবার আমি আমাদের **পুরো Main Architecture**-টা একদম শুরু থেকে শেষ পর্যন্ত **একটা single running example + formula + output** দিয়ে সাজিয়ে দিচ্ছি, যেন তুমি architecture-টা মাথায় visual flow হিসেবে ধরতে পারো।

---

# Trace the Ace — Main Architecture

পুরো system-এর মূল উদ্দেশ্য:

[
\boxed{
\text{Session transcript}
+
\text{Learning Objective}
\rightarrow
P(\text{Student will answer correctly})
}
]

অর্থাৎ আমাদের model শুধু transcript দেখে general student quality predict করবে না।

বরং প্রশ্ন হবে:

> **এই specific session-এ, এই specific learning objective-এর জন্য student আসলে কতটা mastery দেখিয়েছে?**

পুরো architecture:

```text id="5whxdp"
RAW ORDERED TRANSCRIPT
        ↓
CANONICAL TURN RECONSTRUCTION
        ↓
LEARNING OBJECTIVE
        ↓
SPARSE RETRIEVAL + DENSE RETRIEVAL
        ↓
CANDIDATE UNION
        ↓
CROSS-ENCODER RERANKING
        ↓
OBJECTIVE-SPECIFIC TURNS
        ↓
ROLE + TIME EVIDENCE PACK
        ↓
MODERNBERT-BASE (2048)
        ↓
MASTERY LOGIT z_sem
        ↓
BCE + SAME-SESSION PAIRWISE LOSS
        ↓
STRUCTURED FEATURE BRANCH
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
CALIBRATION IF USEFUL
        ↓
FINAL PROBABILITY
```

এখন একটাই example শুরু থেকে শেষ পর্যন্ত চালাই।

---

# STEP 1 — Raw Ordered Transcript

ধরো একটা tutoring session:

```text id="zgts69"
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

এই একই session-এর দুইটা learning objective থাকতে পারে।

```text id="k2g1gv"
Objective A:
Compare fractions with different denominators

Objective B:
Add fractions with different denominators
```

Actual labels ধরো:

```text id="b4pyj5"
Objective A → label = 1

Objective B → label = 0
```

এখন architecture-এর আসল কাজ শুরু।

---

# STEP 2 — Canonical Turn Reconstruction

Raw transcript থেকে আমরা trusted turn table বানাব।

Output:

| session | turn | role    | order | timestamp | text                                           |
| ------- | ---: | ------- | ----: | --------- | ---------------------------------------------- |
| S101    |   U1 | Tutor   |     1 | 10:01     | Which is larger, 1/3 or 1/4?                   |
| S101    |   U2 | Student |     2 | 10:02     | I think 1/4.                                   |
| S101    |   U3 | Tutor   |     3 | 10:03     | Think about the size of each piece.            |
| S101    |   U4 | Student |     4 | 10:04     | Oh, 1/3 is larger.                             |
| S101    |   U5 | Student |     5 | 10:05     | Because thirds are bigger pieces than fourths. |
| S101    |   U6 | Tutor   |     6 | 10:06     | Good.                                          |
| S101    |   U7 | Tutor   |     7 | 10:10     | Now add 1/3 and 1/4.                           |
| S101    |   U8 | Student |     8 | 10:11     | I don't know.                                  |

এখানে মূল information:

[
\boxed{\text{Role + Time + True Order}}
]

এগুলো preserve হলো।

এখন আমরা জানি:

```text id="3c8rbm"
Student wrong answer
        ↓
Tutor hint
        ↓
Student correction
        ↓
Student explanation
```

এই chronology later mastery বুঝতে খুব গুরুত্বপূর্ণ।

---

# STEP 3 — Learning Objective Conditioning

এখন প্রথম objective নিই:

[
O_A=
\text{"Compare fractions with different denominators"}
]

এই objective session-এর প্রতিটা turn-এর সঙ্গে compare হবে:

[
O_A\times U_1
]

[
O_A\times U_2
]

[
...
]

[
O_A\times U_8
]

এখন মূল প্রশ্ন:

> কোন turnগুলো `Compare fractions` objective-এর জন্য relevant?

এখানে দুইটা retrieval branch কাজ করবে।

---

# STEP 4 — Sparse Retrieval

Sparse retrieval exact lexical/math evidence ধরবে।

আমাদের final architecture-এ conceptually:

[
\boxed{
S_{\text{sparse}}
=================

\alpha S_{\text{TFIDF}}
+
\beta S_{\text{char}}
+
\gamma S_{\text{math}}
}
]

এখানে:

[
S_{\text{TFIDF}}
]

= word/phrase similarity

[
S_{\text{char}}
]

= character-level similarity

[
S_{\text{math}}
]

= mathematical token overlap

---

## TF-IDF similarity

Objective vector:

[
\vec O
]

Turn vector:

[
\vec T_i
]

Cosine similarity:

[
\boxed{
S_{\text{TFIDF}}(O,T_i)
=======================

\frac{\vec O\cdot\vec T_i}
{|\vec O||\vec T_i|}
}
]

Toy result:

| Turn | Text                            | Sparse score |
| ---- | ------------------------------- | -----------: |
| U1   | Which is larger, 1/3 or 1/4?    |          .83 |
| U2   | I think 1/4.                    |          .36 |
| U3   | Think about size of each piece. |          .19 |
| U4   | 1/3 is larger.                  |          .63 |
| U5   | Thirds are bigger pieces...     |          .48 |
| U7   | Add 1/3 and 1/4.                |          .60 |

খেয়াল করো:

`U7`-এর score .60।

কারণ:

```text id="9ggti1"
1/3
1/4
fractions
```

math tokens match করছে।

কিন্তু objective comparison, U7 addition।

Sparse এখানেই ভুল করতে পারে।

---

# STEP 5 — Dense Retrieval

এখন Sentence-Transformer meaning ধরবে।

Objective:

```text id="fz2iwm"
Compare fractions with different denominators
```

encode হবে:

[
e_O=f_{\text{ST}}(O)
]

Turn:

```text id="dv185n"
Because thirds are bigger pieces than fourths.
```

encode হবে:

[
e_T=f_{\text{ST}}(T)
]

Dense similarity:

[
\boxed{
S_{\text{dense}}
================

\cos(e_O,e_T)
}
]

Toy output:

| Turn | Dense score |
| ---- | ----------: |
| U1   |         .91 |
| U2   |         .66 |
| U3   |         .78 |
| U4   |         .90 |
| U5   |         .95 |
| U7   |         .46 |

Dense model বুঝল:

> “Thirds are bigger pieces than fourths”

exact `compare fractions` না বললেও meaning strongly related।

---

# STEP 6 — Candidate Union

Sparse branch top turns:

```text id="9cljup"
U1
U4
U7
U5
```

Dense branch:

```text id="j6pmsr"
U5
U1
U4
U3
U2
```

Union:

[
\boxed{
C=
C_{\text{sparse}}
\cup
C_{\text{dense}}
}
]

Final candidate pool:

```text id="y1avwe"
U1
U2
U3
U4
U5
U7
```

এখন full transcript-এর 8 turn থেকে 6 candidate পেলাম।

Real dataset-এ 200+ turns থেকে হয়তো 20–30 candidates হবে।

---

# STEP 7 — Cross-Encoder Reranking

এখন Cross-Encoder objective এবং candidate turn **একসাথে পড়ে**।

Input:

```text id="gyrqx1"
[Objective]
Compare fractions with different denominators

[Turn]
Because thirds are bigger pieces than fourths.
```

Cross-Encoder function:

[
\boxed{
r_i=
f_{\text{CE}}(O,T_i)
}
]

Toy output:

| Rank | Turn | Role    | CE score |
| ---: | ---- | ------- | -------: |
|    1 | U5   | Student |      .97 |
|    2 | U4   | Student |      .94 |
|    3 | U1   | Tutor   |      .92 |
|    4 | U3   | Tutor   |      .83 |
|    5 | U2   | Student |      .72 |
|    6 | U7   | Tutor   |      .21 |

এখানে Cross-Encoder U7-কে নামিয়ে দিল:

[
0.60_{\text{sparse}}
\rightarrow
0.21_{\text{CE}}
]

কারণ বুঝেছে:

```text id="d1v662"
"add 1/3 and 1/4"
```

fractions-related হলেও comparison objective না।

এটাই reranking-এর কাজ।

---

# STEP 8 — Objective-Specific Turns

এখন objective-এর relevant turns পাওয়া গেল:

```text id="dyu3g2"
U1 Tutor   → question
U2 Student → wrong attempt
U3 Tutor   → scaffold
U4 Student → correction
U5 Student → explanation
```

এখন transcript আর session-general না।

এখন এটা:

[
\boxed{\text{Objective-specific evidence}}
]

---

# STEP 9 — Role + Time Evidence Pack

এখন turns-গুলো role + chronology অনুযায়ী organize হবে।

Final evidence pack:

```text id="jd73h6"
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

এখন আমাদের **main row-wise dataset প্রস্তুত**।

এক row:

| response | session | objective         | before      | tutor          | after            | final                | negative    | label |
| -------- | ------- | ----------------- | ----------- | -------------- | ---------------- | -------------------- | ----------- | ----: |
| R1       | S101    | Compare fractions | I think 1/4 | Think about... | 1/3 is larger... | Thirds are bigger... | I think 1/4 |     1 |

---

# STEP 10 — Tokenization

Evidence pack tokenizer-এর মধ্যে যাবে।

ধরো:

[
N_{\text{tokens}}=620
]

620 < 2048।

তাই full input থাকবে।

যদি:

[
N=2500
]

তাহলে priority-based truncation হবে:

```text id="zc9kfu"
Objective
↓
Strong student evidence
↓
Final evidence
↓
Pre/post sequence
↓
Tutor context
↓
weaker duplicates
```

Final:

[
\boxed{N\le2048}
]

Output:

```text id="ernpos"
input_ids
attention_mask
```

---

# STEP 11 — ModernBERT-base

Input:

[
x_i
]

ModernBERT:

[
\boxed{
h_i=
\text{ModernBERT}(x_i)
}
]

যেখানে (h_i) হলো contextual representation।

Toy:

[
h_i=
[0.21,-0.45,0.78,\ldots]
]

এখনো probability না।

---

# STEP 12 — Semantic Mastery Logit

Classification head:

[
\boxed{
z_{\text{sem}}
==============

w^\top h_i+b
}
]

ধরো:

[
z_{\text{sem}}=1.35
]

Sigmoid:

[
p_{\text{sem}}
==============

\sigma(1.35)
]

[
\approx0.794
]

অর্থাৎ ModernBERT evidence দেখে বলছে:

[
\boxed{79.4%}
]

mastery/correctness likelihood।

কিন্তু এটা এখনো final prediction না।

---

# STEP 13 — BCE Loss

Actual label:

[
y=1
]

Probability:

[
p=.794
]

Binary Cross Entropy:

[
\boxed{
L_{\text{BCE}}
==============

*

[
y\log p
+
(1-y)\log(1-p)
]
}
]

Positive case:

[
L_{\text{BCE}}
==============

-\log(.794)
]

[
\approx0.231
]

BCE শেখায়:

> এই individual response-এর probability actual label-এর সঙ্গে মিলাও।

---

# STEP 14 — Same-Session Pairwise Loss

এখন একই session-এর Objective B দেখি।

Objective B:

```text id="u8slnk"
Add fractions with different denominators
```

Student evidence:

```text id="22nttw"
Student:
I don't know.
```

ধরো model logit:

[
z^-=-0.60
]

Objective A correct:

[
z^+=1.35
]

আমরা চাই:

[
\boxed{
z^+>z^-
}
]

Pairwise loss:

[
\boxed{
L_{\text{pair}}
===============

\log
\left(
1+
e^{-(z^+-z^-)}
\right)
}
]

Difference:

[
1.35-(-0.60)=1.95
]

তাই loss ছোট হবে।

কিন্তু যদি model দেয়:

```text id="0z8zmg"
Correct objective  = .8
Wrong objective    = 1.1
```

তাহলে pairwise loss বড় হবে।

অর্থাৎ model punishment পাবে:

> একই session-এ wrong objective-কে correct objective-এর উপরে দিয়েছ।

---

# STEP 15 — Total Training Loss

Final training objective:

[
\boxed{
L
=

L_{\text{BCE}}
+
\lambda_{\text{pair}}
L_{\text{pair}}
}
]

ধরো:

[
L_{\text{BCE}}=.30
]

[
L_{\text{pair}}=.50
]

[
\lambda_{\text{pair}}=.10
]

তাহলে:

[
L
=

.30+.10(.50)
]

[
=\boxed{.35}
]

এই loss backpropagation করবে।

```text id="452dk9"
Total Loss
    ↓
Backpropagation
    ↓
ModernBERT weights update
```

---

# STEP 16 — Parallel Structured Feature Branch

এখন একই response থেকে parallel numerical information বের হবে।

এগুলো তিন family-এর।

```text id="cvuu9a"
Retrieval / Confidence
Tutor / Help
Temporal / Negative
```

---

## Retrieval / Confidence

Example:

```text id="nkra9p"
student_support_max       = .96
student_support_topk_mean = .84
retrieval_margin          = .32
evidence_coverage         = .88
CE_top1                   = .97
```

মানে:

> Evidence objective-এর জন্য strong।

---

## Tutor / Help

```text id="8gmylo"
tutor_support_max         = .81
student_support_max       = .96
tutor_minus_student       = -.15
post_feedback_gain        = +.35
tutor_correction_count    = 1
```

এখন model বুঝতে পারে:

> Student help পেয়েছে, কিন্তু student evidence tutor-এর চেয়ে stronger।

---

## Temporal / Negative

```text id="3j6qeb"
pre_feedback_support   = .30
post_feedback_support  = .86
final_segment_support  = .92
uncertainty_score      = .20
answer_change          = 1
```

এটা বলছে:

```text id="sk20m5"
Initially weak
     ↓
Tutor feedback
     ↓
Student improved
     ↓
Final evidence strong
```

---

# STEP 17 — 20–35 Structured Features

সব feature একসাথে:

[
\boxed{
x_{\text{struct}}
=================

[x_1,x_2,\ldots,x_{30}]
}
]

উদাহরণ row:

| z_sem | support_max | retrieval_margin | tutor_minus_student | post_gain | final_support | uncertainty |
| ----: | ----------: | ---------------: | ------------------: | --------: | ------------: | ----------: |
|  1.35 |         .96 |              .32 |                -.15 |       .35 |           .92 |         .20 |

ModernBERT দিয়েছে **meaning**।

Structured branch দিয়েছে **behaviour/evidence quality**।

---

# STEP 18 — Evidence-Confidence Gate

এখন system decide করবে:

> ModernBERT-এর semantic score কতটা trust করব?

Gate:

[
\boxed{
g=
\sigma
(
w_g^\top x_{\text{confidence}}+b_g
)
}
]

ধরো evidence strong।

Gate:

[
g=.90
]

মানে ModernBERT score highly trusted।

Gated semantic score:

[
g z_{\text{sem}}
]

[
=.90\times1.35
]

[
=\boxed{1.215}
]

Weak evidence হলে gate .20–.30 হতে পারে।

---

# STEP 19 — Fold-Safe Objective Prior

এখন objective historically কতটা easy/hard?

ধরো training fold-এ:

```text id="xzwpjv"
Objective = Compare fractions

100 samples
75 positive
```

Global positive:

[
p_{\text{global}}=.70
]

Smoothed prior:

[
\boxed{
p_o=
\frac{
n_o^+ + \alpha p_{\text{global}}
}{
n_o+\alpha
}
}
]

ধরো:

[
\alpha=20
]

তাহলে:

[
p_o=
\frac{75+20(.70)}
{100+20}
]

# [

\frac{89}{120}
]

[
\approx.742
]

Objective prior:

[
\boxed{p_o=.742}
]

Logit:

[
\boxed{
z_{\text{prior}}
================

\log
\frac{p_o}{1-p_o}
}
]

roughly:

[
z_{\text{prior}}\approx1.06
]

Important:

Validation row-এর label এটা calculate করতে ব্যবহার হবে না।

এই জন্য:

[
\boxed{\text{Fold-safe}}
]

---

# STEP 20 — Simple Fusion

এখন আমাদের কাছে:

```text id="ze68p3"
Semantic logit    = 1.35
Gate              = .90
Prior logit       = 1.06
Structured        = 20–35 features
```

Fusion:

[
\boxed{
z_{\text{fusion}}
=================

\beta_0
+
\beta_1z_{\text{prior}}
+
\beta_2(gz_{\text{sem}})
+
\beta^\top x_{\text{struct}}
}
]

ধরো final fused logit:

[
\boxed{
z_{\text{fusion}}=1.50
}
]

---

# STEP 21 — Neural Probability

Sigmoid:

[
\boxed{
p_{\text{neural}}
=================

\sigma(z_{\text{fusion}})
}
]

# [

\sigma(1.50)
]

[
\approx
\boxed{0.818}
]

অর্থাৎ complete neural system বলছে:

> 81.8% chance correct।

---

# STEP 22 — Separate TF-IDF Logistic Model

আমরা proven TF-IDF model বাদ দিচ্ছি না।

Separate branch:

```text id="366791"
Objective + transcript/evidence
        ↓
TF-IDF
        ↓
Logistic Regression
        ↓
Probability
```

Logistic formula:

[
\boxed{
p_{\text{TFIDF}}
================

\sigma
(
w^\top x_{\text{TFIDF}}+b
)
}
]

ধরো:

[
p_{\text{TFIDF}}=.71
]

এখন:

```text id="hkv2yh"
Neural = .818
TF-IDF = .710
```

---

# STEP 23 — OOF Predictions

5-fold session-grouped validation হবে।

প্রতিটি training sample prediction পাবে এমন model থেকে যেটা ওই session training-এ দেখেনি।

Output:

| response | label | neural_OOF | tfidf_OOF |
| -------- | ----: | ---------: | --------: |
| R1       |     1 |       .818 |      .710 |
| R2       |     0 |       .310 |      .460 |
| R3       |     1 |       .770 |      .730 |
| R4       |     0 |       .440 |      .500 |

এই OOF predictions দিয়ে blend weight select করা হবে।

---

# STEP 24 — OOF Blend

Formula:

[
\boxed{
p_{\text{blend}}
================

w p_{\text{neural}}
+
(1-w)p_{\text{TFIDF}}
}
]

OOF Log Loss minimize করে best (w) বের করব।

ধরো:

[
w=.80
]

তাহলে:

[
p_{\text{blend}}
================

.80(.818)+.20(.710)
]

[
=.6544+.142
]

# [

\boxed{.7964}
]

অর্থাৎ blended prediction:

[
79.64%
]

---

# STEP 25 — Calibration

এখন check করব probability confidence ঠিক আছে কি না।

যদি model systematically overconfident হয়:

```text id="nkfsr5"
Prediction .95
Reality ~.85
```

তাহলে calibration useful হতে পারে।

---

## Temperature Scaling

Blend probability logit:

[
z=
\log
\frac{p}{1-p}
]

Temperature:

[
\boxed{
p_{\text{cal}}
==============

\sigma
\left(
\frac{z}{T}
\right)
}
]

যদি:

[
T>1
]

prediction softer।

---

## Platt Scaling

[
\boxed{
p_{\text{cal}}
==============

\sigma(az+b)
}
]

কিন্তু calibration **mandatory না**।

আমরা compare করব:

[
LL_{\text{uncalibrated}}
]

vs

[
LL_{\text{calibrated}}
]

যদি calibrated OOF Log Loss lower:

[
\boxed{\text{Keep calibration}}
]

না হলে বাদ।

---

# STEP 26 — Final Probability

ধরো blend:

[
.796
]

Calibration শেষে:

[
.780
]

তাহলে final submission:

| response_id | probability |
| ----------- | ----------: |
| R1          |   **0.780** |

এই:

[
\boxed{0.780}
]

হলো competition-এর final prediction।

---

# এখন Objective B-ও দেখি

Same session:

```text id="z977cu"
Objective:
Add fractions with different denominators

Student:
I don't know.
```

System হয়তো:

```text id="7jw89u"
Dense evidence      = weak
Student support     = low
Uncertainty         = high
Tutor dominance     = high
Final support       = low
```

ModernBERT:

[
z_{\text{sem}}=-.75
]

Gate:

[
g=.35
]

Prior:

[
p_o=.68
]

Fusion:

[
p_{\text{neural}}=.36
]

TF-IDF:

[
p_{\text{TFIDF}}=.50
]

Blend:

[
p_{\text{blend}}=.39
]

Final:

[
\boxed{.40}
]

Same session output:

| Objective         | Final probability |
| ----------------- | ----------------: |
| Compare fractions |           **.78** |
| Add fractions     |           **.40** |

এটাই আমাদের architecture-এর আসল success condition।

Old baseline হয়তো:

```text id="1mjjcm"
Compare → .76
Add     → .74
```

দিত।

কারণ whole-session positive impression dominate করত।

New architecture:

```text id="2p1nsk"
Compare → .78
Add     → .40
```

কারণ objective-specific evidence আলাদা।

---

# পুরো system mathematically compact করলে

Input:

[
S=\text{session}
]

[
O=\text{objective}
]

### Retrieval

[
C=
TopK_{\text{sparse}}(S,O)
\cup
TopK_{\text{dense}}(S,O)
]

### Cross-Encoder

[
E=
TopK
\left(
f_{\text{CE}}(O,C)
\right)
]

### Evidence Pack

[
X=
Pack(E,\text{role},\text{time})
]

### ModernBERT

[
h=
ModernBERT(X)
]

### Semantic logit

[
z_{\text{sem}}
==============

w^\top h+b
]

### Main training

[
L_{\text{BCE}}
==============

BCE(\sigma(z_{\text{sem}}),y)
]

[
L_{\text{pair}}
===============

\log
\left(
1+e^{-(z^+-z^-)}
\right)
]

[
L=
L_{\text{BCE}}
+
\lambda_{\text{pair}}L_{\text{pair}}
]

### Structured features

[
x_{\text{struct}}
=================

f_{\text{features}}(E)
]

### Confidence gate

[
g=
\sigma
(
w_g^\top x_{\text{confidence}}+b_g
)
]

### Objective prior

[
p_o=
\frac{
n_o^+ + \alpha p_{\text{global}}
}{
n_o+\alpha
}
]

[
z_{\text{prior}}
================

\operatorname{logit}(p_o)
]

### Fusion

[
z_{\text{fusion}}
=================

\beta_0
+
\beta_1z_{\text{prior}}
+
\beta_2gz_{\text{sem}}
+
\beta^\top x_{\text{struct}}
]

### Neural probability

[
p_N=
\sigma(z_{\text{fusion}})
]

### TF-IDF model

[
p_T=
\sigma
(
w_T^\top x_{\text{TFIDF}}+b_T
)
]

### Blend

[
p_B=
w p_N+(1-w)p_T
]

### Optional calibration

[
p_{\text{final}}
================

Calibrate(p_B)
]

Final:

[
\boxed{
P(y=1\mid S,O)
==============

p_{\text{final}}
}
]

---

# Architecture-টা আসলে পাঁচটা intelligence layer

### Layer A — Find the right evidence

```text id="w8rq5m"
Sparse
+
Dense
+
CrossEncoder
```

প্রশ্ন:

> Objective-এর জন্য relevant conversation কোথায়?

---

### Layer B — Understand evidence structure

```text id="4ui703"
Role
+
Time
+
Before/After
+
Tutor/Student
```

প্রশ্ন:

> Evidence কে দিয়েছে এবং কোন sequence-এ এসেছে?

---

### Layer C — Understand semantic mastery

```text id="7vk6up"
ModernBERT
+
Pairwise learning
```

প্রশ্ন:

> Student-এর actual mastery evidence কী বলছে?

---

### Layer D — Correct model context

```text id="47lpgs"
Structured features
+
Evidence gate
+
Objective prior
```

প্রশ্ন:

> Semantic evidence কতটা trustworthy, tutor সাহায্য কতটা, objective historically কত কঠিন?

---

### Layer E — Final robust probability

```text id="izcpk5"
Neural
+
TF-IDF
+
OOF blend
+
Calibration
```

প্রশ্ন:

> সব complementary signal combine করলে safest final probability কত?

---

# সবচেয়ে গুরুত্বপূর্ণ architectural philosophy

আমাদের architecture বলছে না:

[
\text{Transcript}
\rightarrow
\text{Prediction}
]

বরং বলছে:

[
\boxed{
\text{Transcript}
\rightarrow
\text{Objective-specific evidence}
\rightarrow
\text{Student behaviour}
\rightarrow
\text{Semantic mastery}
\rightarrow
\text{Confidence correction}
\rightarrow
\text{Final probability}
}
]

এটাই এর সবচেয়ে বড় strength।

কারণ আমাদের baseline-এর মূল failure ছিল:

[
\boxed{
\text{Session identity/general transcript signal}

>

\text{Objective-specific mastery}
}
]

আর Main Architecture পুরো pipeline-টাই উল্টে দিয়েছে:

[
\boxed{
\text{Objective-specific evidence}

>

\text{general session impression}
}
]

তাই architecture-এর প্রতিটা component একই central problem-এর different part solve করছে—এ কারণেই এটা শুধু complicated architecture না; **internally coherent architecture**।

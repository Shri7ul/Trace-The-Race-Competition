# Trace the Ace — Mathematical Architecture from Step 11 to Final Probability

এই document-এ Cross-Encoder-এর পর থেকে পুরো architecture-টা mathematically এবং architecturally explain করা হয়েছে।

```text
Evidence Pack
    ↓
ModernBERT
    ↓
Semantic Mastery Logit
    ↓
BCE + Same-Session Pairwise Loss
    ↓
Structured Feature Branch
    ↓
Evidence-Confidence Gate
    ↓
Fold-Safe Objective Prior
    ↓
Simple Fusion
    ↓
Neural Probability
    ↓
TF-IDF Logistic Branch
    ↓
OOF Blend
    ↓
Optional Calibration
    ↓
Final Probability
```

---

# 0. Architecture Graph — Important View

Step 11–26 পুরোপুরি straight line না। কিছু branch parallel-এ কাজ করে।

```text
                         ┌─────────────────────────────┐
                         │  EVIDENCE PACK / TEXT       │
                         └─────────────┬───────────────┘
                                       │
                                       ▼
                                ModernBERT
                                       │
                                       ▼
                                  z_sem
                                  /   \
                                 /     \
                              BCE     Pairwise


Retrieval results ────────────────► Structured Features
                                       │
                                       ▼
                              Confidence Gate
                                       │
Objective statistics ────────────► Fold-safe Prior
                                       │
                         z_sem ─────────┤
                                       ▼
                                    Fusion
                                       │
                                       ▼
                               Neural Probability


Text / Objective ─────────────────► TF-IDF Logistic
                                       │
                                       ▼
                               TF-IDF Probability

             Neural Probability + TF-IDF Probability
                              │
                              ▼
                           OOF Blend
                              │
                              ▼
                         Calibration
                              │
                              ▼
                     FINAL PROBABILITY
```

---

# 1. Fixed Running Example

## Response A

```text
response_id = R1
session_id  = S101

Objective:
Compare fractions with different denominators

Evidence:
Student before:
"I think 1/4."

Tutor:
"Think about the size of each piece."

Student after:
"Oh, 1/3 is larger."

Final student:
"Thirds are bigger pieces than fourths."

Label:
y = 1
```

## Response B

একই session-এর আরেক objective:

```text
response_id = R2
session_id  = S101

Objective:
Add fractions with different denominators

Evidence:
Student:
"I don't know."

Label:
y = 0
```

অর্থাৎ:

$$
R_1: y=1
$$

$$
R_2: y=0
$$

এই pair-টাই Same-Session Pairwise Loss-এর জন্য ব্যবহার হবে।

---

# PART 1 — ModernBERT Semantic Branch

# STEP 11 — Evidence Pack → ModernBERT Representation

আগের stage শেষে evidence pack tokenizer-এর মধ্যে দিয়ে গেছে। Response \(i\)-এর tokenized input:

$$
x_i
$$

Conceptually:

```text
[OBJECTIVE]
Compare fractions...

[STUDENT_BEFORE]
I think 1/4.

[TUTOR]
Think about...

[STUDENT_AFTER]
1/3 is larger.

[FINAL]
Thirds are bigger pieces...
```

Tokenizer এটাকে token IDs-এ convert করে, যেমন:

```text
[4712, 223, 817, 991, ...]
```

এর সাথে `attention_mask` থাকবে।

ModernBERT function:

$$
\boxed{
h_i = \operatorname{ModernBERT}(x_i)
}
$$

এখানে:

- \(x_i\) = tokenized evidence input
- \(h_i\) = ModernBERT-এর contextual representation

## \(h_i\) আসলে কী?

ModernBERT সরাসরি probability দেয় না। এটা evidence-এর learned vector representation দেয়। বোঝার জন্য toy example:

$$
h_i=[0.8,-0.4,0.6,0.9]
$$

এই vector-এর individual value-এর direct human meaning নেই। পুরো vector একসাথে encode করে objective-specific semantic evidence।

---

# STEP 12 — ModernBERT Representation → Semantic Mastery Logit

ModernBERT representation-এর ওপর classification head বসে।

$$
\boxed{
z_{\text{sem}}=w^\top h_i+b
}
$$

এখানে:

- \(h_i\) = ModernBERT representation
- \(w\) = learned classification weights
- \(b\) = learned bias
- \(z_{\text{sem}}\) = semantic mastery logit

## Dot Product Example

ধরি:

$$
h=[0.8,-0.4,0.6,0.9]
$$

$$
w=[0.7,-0.2,0.5,0.6]
$$

$$
b=-0.13
$$

তাহলে:

$$
w^\top h=0.7(0.8)+(-0.2)(-0.4)+0.5(0.6)+0.6(0.9)
$$

$$
=0.56+0.08+0.30+0.54=1.48
$$

Bias add করলে:

$$
z_{\text{sem}}=1.48-0.13
$$

$$
\boxed{z_{\text{sem}}=1.35}
$$

এই `1.35` probability না; এটা raw logit।

## Logit → Probability

Logit theoretically:

$$
-\infty<z<+\infty
$$

Probability হতে হবে:

$$
0\le p\le1
$$

তাই sigmoid:

$$
\boxed{
\sigma(z)=\frac{1}{1+e^{-z}}
}
$$

আমাদের:

$$
p_{\text{sem}}=\sigma(1.35)
$$

$$
=\frac{1}{1+e^{-1.35}}
$$

যেহেতু:

$$
e^{-1.35}\approx0.259
$$

তাই:

$$
p_{\text{sem}}\approx\frac{1}{1.259}\approx0.794
$$

$$
\boxed{p_{\text{sem}}\approx0.794}
$$

অর্থাৎ semantic branch প্রায় **79.4% positive/correct likelihood** দিচ্ছে। কিন্তু:

$$
\boxed{p_{\text{sem}}\neq p_{\text{final}}}
$$

---

# PART 2 — BCE Loss

# STEP 13 — Binary Cross Entropy

Response A-এর actual label:

$$
y=1
$$

Prediction:

$$
p=0.794
$$

Binary Cross Entropy:

$$
\boxed{
L_{\text{BCE}}=-\left[y\log(p)+(1-y)\log(1-p)\right]
}
$$

এখন \(y=1\):

$$
L_{\text{BCE}}=-\left[1\log(0.794)+0\log(1-0.794)\right]
$$

$$
L_{\text{BCE}}=-\log(0.794)
$$

$$
\boxed{L_{\text{BCE}}\approx0.231}
$$

## BCE কী শেখায়?

- correct confident prediction → small loss
- wrong confident prediction → large loss

Sigmoid + BCE-এর useful derivative:

$$
\boxed{
\frac{\partial L}{\partial z}=p-y
}
$$

আমাদের:

$$
0.794-1=-0.206
$$

Negative gradient optimizer-কে \(z_{\text{sem}}\) বাড়ানোর দিকে push করবে।

## Negative Row Example

Response B:

$$
y=0
$$

ধরি:

$$
z^-=-0.60
$$

তাহলে:

$$
p^-=\sigma(-0.60)\approx0.354
$$

Gradient:

$$
p-y=0.354-0=0.354
$$

Optimizer negative sample-এর logit নিচে নামানোর দিকে push করবে।

সুতরাং BCE শেখায়:

```text
Positive response → logit ওপরে নাও
Negative response → logit নিচে নামাও
```

---

# PART 3 — Same-Session Pairwise Loss

# STEP 14 — Pairwise Ranking

Same session `S101`:

$$
z^+=1.35
$$

$$
z^-=-0.60
$$

আমাদের desired condition:

$$
\boxed{z^+>z^-}
$$

## Pairwise Margin

$$
\boxed{d=z^+-z^-}
$$

আমাদের:

$$
d=1.35-(-0.60)=1.95
$$

$$
\boxed{d=1.95}
$$

Positive margin মানে correct objective negative objective-এর উপরে।

## Pairwise Loss

$$
\boxed{
L_{\text{pair}}=\log\left(1+e^{-(z^+-z^-)}\right)
}
$$

যেহেতু \(d=z^+-z^-\):

$$
L_{\text{pair}}=\log(1+e^{-d})
$$

আমাদের:

$$
L_{\text{pair}}=\log(1+e^{-1.95})
$$

$$
e^{-1.95}\approx0.142
$$

$$
L_{\text{pair}}=\log(1.142)\approx0.133
$$

$$
\boxed{L_{\text{pair}}\approx0.133}
$$

## Wrong Ordering Example

ধরি:

$$
z^+=0.40,\qquad z^-=1.00
$$

তাহলে:

$$
d=-0.60
$$

$$
L_{\text{pair}}=\log(1+e^{0.60})\approx1.037
$$

$$
\boxed{L_{\text{pair}}\approx1.037}
$$

অর্থাৎ wrong ordering হলে loss অনেক বড়।

## Pairwise Gradient

$$
L=\log(1+e^{-d})
$$

$$
\boxed{
\frac{\partial L}{\partial d}=-\frac{1}{1+e^d}
}
$$

Margin ছোট বা negative হলে gradient strong। Model-কে push করে:

$$
z^+\uparrow
$$

$$
z^-\downarrow
$$

---

# PART 4 — Total Semantic Training Loss

# STEP 15 — BCE + Pairwise

Combined loss:

$$
\boxed{
L_{\text{total}}=L_{\text{BCE}}+\lambda_{\text{pair}}L_{\text{pair}}
}
$$

এখানে \(\lambda_{\text{pair}}\) pairwise importance control করে। Initial search range হিসেবে:

$$
0.05\le\lambda_{\text{pair}}\le0.30
$$

একটি reasonable range।

## Full Toy Calculation

Positive row:

$$
L_A\approx0.231
$$

Negative row:

$$
p_B=0.354
$$

$$
L_B=-\log(1-0.354)=-\log(0.646)\approx0.437
$$

Mean BCE:

$$
L_{\text{BCE}}=\frac{0.231+0.437}{2}\approx0.334
$$

Pairwise:

$$
L_{\text{pair}}=0.133
$$

ধরি:

$$
\lambda_{\text{pair}}=0.10
$$

তাহলে:

$$
L_{\text{total}}=0.334+0.10(0.133)
$$

$$
=0.334+0.0133
$$

$$
\boxed{L_{\text{total}}\approx0.347}
$$

এই scalar loss backpropagation হয়।

```text
0.347
  ↓
Gradient calculation
  ↓
Classification-head weights update
  ↓
ModernBERT weights update
  ↓
Next batch
```

এই পর্যন্ত semantic branch শেখে:

$$
\boxed{
\text{Evidence Pack}\rightarrow z_{\text{sem}}
}
$$

---

# PART 5 — Structured Feature Branch

এই branch ModernBERT hidden vector থেকে আসে না। এটা parallel-এ আসে:

```text
Cross-Encoder scores
Role
Turn order
Retrieval scores
Tutor/student separation
Evidence positions
Feedback sequence
```

থেকে।

---

# STEP 16 — Retrieval / Confidence Features

Cross-Encoder result:

| Turn | Role | CE Score |
|---|---|---:|
| U5 | Student | 0.97 |
| U4 | Student | 0.94 |
| U1 | Tutor | 0.92 |
| U3 | Tutor | 0.83 |
| U2 | Student | 0.72 |
| U7 | Tutor / irrelevant | 0.21 |

## Feature 1 — Student Support Max

Student scores:

$$
[0.97,0.94,0.72]
$$

$$
\boxed{
\text{student\_support\_max}=\max(0.97,0.94,0.72)=0.97
}
$$

## Feature 2 — Student Support Top-k Mean

$$
\text{student\_support\_topk\_mean}=\frac{0.97+0.94+0.72}{3}
$$

$$
=\frac{2.63}{3}\approx0.877
$$

$$
\boxed{\text{student\_support\_topk\_mean}\approx0.877}
$$

## Feature 3 — Tutor Support Max

Tutor scores:

$$
0.92,\quad0.83
$$

$$
\boxed{\text{tutor\_support\_max}=0.92}
$$

## Feature 4 — Tutor Minus Student

$$
\boxed{
\text{tutor\_minus\_student}=\text{tutor\_max}-\text{student\_max}
}
$$

$$
=0.92-0.97=-0.05
$$

$$
\boxed{\text{tutor\_minus\_student}=-0.05}
$$

Negative value মানে strongest student evidence strongest tutor evidence-এর চেয়ে stronger।

## Feature 5 — Retrieval Margin

Toy definition:

$$
\boxed{
\text{retrieval\_margin}=\text{top relevant score}-\text{hard negative score}
}
$$

$$
=0.97-0.21=0.76
$$

$$
\boxed{\text{retrieval\_margin}=0.76}
$$

## Feature 6 — Evidence Coverage

ধরি desired categories:

```text
Student before        ✅
Tutor context         ✅
Student after         ✅
Final student         ✅
Negative / uncertain  ✅
```

Toy definition:

$$
\boxed{
\text{coverage}=\frac{\text{available evidence categories}}{\text{desired evidence categories}}
}
$$

$$
\text{coverage}=\frac{5}{5}=1.0
$$

$$
\boxed{\text{coverage}=1.0}
$$

## Temporal Features

Pre-feedback support:

$$
\text{support}_{\text{before}}=0.72
$$

Post-feedback support:

$$
\text{support}_{\text{after}}=\frac{0.94+0.97}{2}=0.955
$$

Post-feedback gain:

$$
\boxed{
\text{post\_feedback\_gain}=\text{support}_{\text{after}}-\text{support}_{\text{before}}
}
$$

$$
=0.955-0.72=0.235
$$

$$
\boxed{\text{post\_feedback\_gain}=0.235}
$$

Final support:

$$
\boxed{\text{final\_support}=0.97}
$$

ধরি uncertainty mechanism দেয়:

$$
\boxed{\text{uncertainty}=0.10}
$$

---

# STEP 17 — 20–35 Structured Feature Vector

সব features combine করে:

$$
\boxed{
x_{\text{struct}}=[x_1,x_2,\ldots,x_d]
}
$$

যেখানে:

$$
d\approx20\text{–}35
$$

Simplified toy vector:

$$
x_{\text{struct}}=[0.97,0.877,0.76,1.00,-0.05,0.235,0.97,0.10]
$$

Conceptually:

$$
\boxed{\text{ModernBERT}=\text{Semantic Meaning}}
$$

$$
\boxed{\text{Structured Features}=\text{Evidence Behaviour + Confidence}}
$$

---

# PART 6 — Evidence-Confidence Gate

# STEP 18 — Semantic Score কতটা Trust করব?

Gate-এর কাজ ModernBERT-এর semantic score কতটা trust করা উচিত তা learn করা।

Strong evidence:

$$
g\rightarrow1
$$

Weak evidence:

$$
g\rightarrow0
$$

Formula:

$$
\boxed{
g=\sigma\left(w_g^\top x_{\text{confidence}}+b_g\right)
}
$$

## Gate Input

ধরি:

$$
x_c=[0.97,0.76,1.00,0.97,-0.05]
$$

Toy learned weights:

$$
w_g=[1.2,0.8,0.6,1.0,-0.4]
$$

Bias:

$$
b_g=-2
$$

Pre-activation:

$$
a_g=w_g^\top x_c+b_g
$$

$$
=1.2(0.97)+0.8(0.76)+0.6(1.00)+1.0(0.97)+(-0.4)(-0.05)-2
$$

$$
=1.164+0.608+0.600+0.970+0.020-2
$$

$$
a_g=1.362
$$

Sigmoid:

$$
g=\sigma(1.362)\approx0.796
$$

$$
\boxed{g\approx0.796}
$$

Gated semantic logit:

$$
gz_{\text{sem}}=0.796(1.35)\approx1.075
$$

$$
\boxed{gz_{\text{sem}}\approx1.075}
$$

Weak evidence হলে, ধরো \(g=0.20\):

$$
gz_{\text{sem}}=0.20(1.35)=0.27
$$

অর্থাৎ semantic branch-এর influence কমে যাবে।

---

# PART 7 — Fold-Safe Objective Prior

# STEP 19 — Objective Difficulty / Historical Tendency

ধরি current training fold-এ:

```text
Objective A seen = 100 times
Positive         = 75
```

Global positive rate:

$$
p_{\text{global}}=0.70
$$

Naive prior:

$$
75/100=0.75
$$

Rare objectives-এর জন্য smoothing দরকার।

## Smoothed Objective Prior

$$
\boxed{
p_o=\frac{n_o^++\alpha p_{\text{global}}}{n_o+\alpha}
}
$$

আমাদের:

$$
n_o^+=75,\quad n_o=100,\quad \alpha=20,\quad p_{\text{global}}=0.70
$$

তাই:

$$
p_o=\frac{75+20(0.70)}{100+20}=\frac{89}{120}\approx0.742
$$

$$
\boxed{p_o\approx0.742}
$$

## Rare Objective Example

ধরি 2 samples, 2 positive। Naive prior:

$$
2/2=1.0
$$

Smoothed:

$$
p_o=\frac{2+20(0.70)}{2+20}=\frac{16}{22}\approx0.727
$$

$$
\boxed{p_o\approx0.727}
$$

Rare objective global prior-এর দিকে shrink করে।

## Prior Probability → Prior Logit

$$
\boxed{
z_{\text{prior}}=\log\left(\frac{p_o}{1-p_o}\right)
}
$$

আমাদের:

$$
z_{\text{prior}}=\log\left(\frac{0.742}{0.258}\right)=\log(2.876)\approx1.06
$$

$$
\boxed{z_{\text{prior}}\approx1.06}
$$

## Fold-Safe কেন?

```text
Fold-1 TRAIN labels
       ↓
Objective statistics
       ↓
Fold-safe prior
       ↓
Fold-1 VALID prediction
```

Validation labels prior তৈরিতে ব্যবহার হবে না।

---

# PART 8 — Simple Fusion

# STEP 20 — Semantic + Gate + Prior + Structured Features

Available signals:

```text
Semantic logit         = 1.35
Evidence gate          = 0.796
Objective prior logit  = 1.06
Structured features    = 20–35 values
```

Fusion:

$$
\boxed{
z_{\text{fusion}}=\beta_0+\beta_1z_{\text{prior}}+\beta_2(gz_{\text{sem}})+\beta^\top x_{\text{struct}}
}
$$

## Simplified Toy Fusion

ধরি structured vector-এর 3টি feature:

$$
x_s=[0.235,0.10,-0.05]
$$

Learned coefficients:

$$
\beta_0=-0.20
$$

$$
\beta_1=0.40
$$

$$
\beta_2=1.10
$$

Structured weights:

$$
\beta_s=[0.50,-0.60,-0.40]
$$

আমাদের gated semantic logit:

$$
gz_{\text{sem}}=1.075
$$

তাই:

$$
z_{\text{fusion}}=-0.20+0.40(1.06)+1.10(1.075)+0.50(0.235)-0.60(0.10)-0.40(-0.05)
$$

Individual contributions:

$$
0.40(1.06)=0.424
$$

$$
1.10(1.075)=1.1825
$$

$$
0.50(0.235)=0.1175
$$

$$
-0.60(0.10)=-0.060
$$

$$
-0.40(-0.05)=+0.020
$$

সব যোগ করলে:

$$
z_{\text{fusion}}\approx1.484
$$

$$
\boxed{z_{\text{fusion}}\approx1.484}
$$

## Contribution Interpretation

| Signal | Contribution |
|---|---:|
| Prior | +0.424 |
| Gated semantic | +1.183 |
| Post-feedback gain | +0.118 |
| Uncertainty | -0.060 |
| Student stronger than tutor | +0.020 |

## Gate/Fusion কীভাবে শিখবে?

Gate weights \(w_g\) এবং fusion weights \(\beta\) supervisedভাবে learn করতে হবে। Clean execution:

```text
PHASE A
ModernBERT semantic model
BCE + Pairwise
        ↓
OOF / fold-safe z_sem

PHASE B
z_sem
+ structured features
+ fold-safe prior
        ↓
Gate + Fusion
        ↓
Lightweight BCE training
```

---

# PART 9 — Neural Probability

# STEP 21

Fusion logit:

$$
z_{\text{fusion}}=1.484
$$

Sigmoid:

$$
p_{\text{neural}}=\sigma(1.484)=\frac{1}{1+e^{-1.484}}
$$

যেহেতু:

$$
e^{-1.484}\approx0.227
$$

তাই:

$$
p_{\text{neural}}\approx\frac{1}{1.227}\approx0.815
$$

$$
\boxed{p_{\text{neural}}\approx0.815}
$$

এখন neural probability-এর মধ্যে আছে semantic understanding + evidence confidence + tutor/student behaviour + temporal behaviour + negative evidence + objective prior।

---

# PART 10 — TF-IDF Logistic Parallel Model

# STEP 22

```text
Objective + selected text
        ↓
TF-IDF vector
        ↓
Logistic Regression
        ↓
TF-IDF Probability
```

Raw score:

$$
\boxed{z_T=w_T^\top x_{\text{TFIDF}}+b_T}
$$

Probability:

$$
\boxed{p_T=\sigma(z_T)}
$$

ধরি:

$$
z_T=0.90
$$

তাহলে:

$$
p_T=\sigma(0.90)=\frac{1}{1+e^{-0.90}}\approx0.711
$$

$$
\boxed{p_T\approx0.711}
$$

| Model | Probability |
|---|---:|
| Neural Architecture | 0.815 |
| TF-IDF Logistic | 0.711 |

---

# PART 11 — OOF Predictions

# STEP 23 — Out-of-Fold Prediction

5 session-grouped folds:

```text
Fold 1
Fold 2
Fold 3
Fold 4
Fold 5
```

Fold 1:

```text
Train: Fold 2 + Fold 3 + Fold 4 + Fold 5
Predict: Fold 1
```

Fold 2:

```text
Train: Fold 1 + Fold 3 + Fold 4 + Fold 5
Predict: Fold 2
```

প্রতিটি row এমন model থেকে prediction পায় যেটা ওই row-এর session training-এ দেখেনি।

## OOF Table

| response_id | label | neural_OOF | tfidf_OOF |
|---|---:|---:|---:|
| R1 | 1 | 0.815 | 0.711 |
| R2 | 0 | 0.310 | 0.460 |
| R3 | 1 | 0.770 | 0.730 |
| R4 | 0 | 0.440 | 0.500 |

Training predictions overly optimistic হতে পারে, তাই blend weight OOF predictions থেকে শেখানো safer।

---

# PART 12 — OOF Blend

# STEP 24 — Neural + TF-IDF

$$
\boxed{
p_{\text{blend}}=wp_N+(1-w)p_T
}
$$

Best weight manually fixed না। OOF Log Loss minimize করে:

$$
\boxed{
w^*=\arg\min_{0\le w\le1}LL(p_{\text{blend}})
}
$$

প্রতি row:

$$
p_i(w)=wp_{N,i}+(1-w)p_{T,i}
$$

OOF Log Loss:

$$
\boxed{
LL(w)=-\frac{1}{N}\sum_{i=1}^{N}\left[y_i\log(p_i(w))+(1-y_i)\log(1-p_i(w))\right]
}
$$

Toy search:

```text
w = 0.00
w = 0.05
w = 0.10
...
w = 1.00
```

ধরি best:

$$
w=0.80
$$

আমাদের:

$$
p_N=0.815,\qquad p_T=0.711
$$

তাই:

$$
p_B=0.80(0.815)+0.20(0.711)
$$

$$
=0.652+0.1422
$$

$$
\boxed{p_B=0.7942}
$$

---

# PART 13 — Calibration

# STEP 25 — Probability Confidence Correction

Blend probability:

$$
p_B=0.7942
$$

প্রশ্ন: model যখন 79.4% বলে, similar cases-এ বাস্তবে কি প্রায় 79% positive হয়?

যদি model overconfident হয়, calibration useful হতে পারে। Calibration mandatory না।

## Temperature Scaling

Probability থেকে logit:

$$
\boxed{
z_B=\log\left(\frac{p_B}{1-p_B}\right)
}
$$

আমাদের:

$$
1-p_B=0.2058
$$

$$
\frac{0.7942}{0.2058}\approx3.86
$$

$$
z_B=\log(3.86)\approx1.35
$$

$$
\boxed{z_B\approx1.35}
$$

Temperature scaling:

$$
\boxed{
p_{\text{cal}}=\sigma\left(\frac{z_B}{T}\right)
}
$$

যদি:

$$
T=1
$$

তাহলে no change।

যদি:

$$
T=1.15
$$

তাহলে:

$$
\frac{z_B}{T}=\frac{1.35}{1.15}\approx1.174
$$

$$
p_{\text{cal}}=\sigma(1.174)\approx0.764
$$

$$
\boxed{p_{\text{cal}}\approx0.764}
$$

Probability softer:

$$
0.794\rightarrow0.764
$$

## Platt Scaling

Alternative:

$$
\boxed{p_{\text{cal}}=\sigma(az+b)}
$$

Calibration keep করব only if:

$$
\boxed{LL_{\text{calibrated}}<LL_{\text{uncalibrated}}}
$$

না হলে:

$$
p_{\text{final}}=p_{\text{blend}}
$$

---

# PART 14 — Final Probability

# STEP 26

ধরি calibration useful:

$$
p_{\text{final}}=0.764
$$

| response_id | final_probability |
|---|---:|
| R1 | 0.764 |

অর্থাৎ:

$$
\boxed{P(y=1\mid S101,O_A)=0.764}
$$

এটাই final competition probability।

---

# PART 15 — Same Session, Different Objective

Objective B:

```text
Add fractions
```

Actual:

$$
y=0
$$

ধরি:

$$
z_{\text{sem}}=-0.60
$$

$$
p_{\text{sem}}=\sigma(-0.60)\approx0.354
$$

Evidence weak:

$$
g=0.30
$$

Gated semantic:

$$
gz_{\text{sem}}=0.30(-0.60)=-0.18
$$

Suppose prior:

$$
z_{\text{prior}}=0.50
$$

Structured evidence negative contribution দেয়। Fusion শেষে:

$$
z_{\text{fusion}}=-0.50
$$

Neural:

$$
p_N=\sigma(-0.50)\approx0.378
$$

TF-IDF:

$$
p_T=0.48
$$

Blend:

$$
p_B=0.80(0.378)+0.20(0.48)
$$

$$
=0.3024+0.096=0.3984
$$

$$
\boxed{p_B=0.3984}
$$

Calibration শেষে roughly:

$$
\boxed{p_{\text{final}}\approx0.40}
$$

Same session:

| Objective | Final Probability |
|---|---:|
| Compare fractions | **0.76** |
| Add fractions | **0.40** |

Difference:

$$
0.76-0.40=0.36
$$

$$
\boxed{0.36}
$$

এটাই objective-specific separation।

---

# PART 16 — Full Step 11–26 Equation Chain

## 1. Evidence → ModernBERT

$$
\boxed{h_i=\operatorname{ModernBERT}(x_i)}
$$

## 2. Semantic Logit

$$
\boxed{z_{\text{sem}}=w^\top h_i+b}
$$

## 3. Semantic Probability

$$
\boxed{p_{\text{sem}}=\sigma(z_{\text{sem}})}
$$

## 4. BCE

$$
\boxed{L_{\text{BCE}}=-\left[y\log(p)+(1-y)\log(1-p)\right]}
$$

## 5. Same-Session Pairwise Loss

$$
\boxed{L_{\text{pair}}=\log\left(1+e^{-(z^+-z^-)}\right)}
$$

## 6. Total Semantic Training Loss

$$
\boxed{L=L_{\text{BCE}}+\lambda_{\text{pair}}L_{\text{pair}}}
$$

## 7. Structured Evidence Vector

$$
\boxed{x_{\text{struct}}=f(\text{retrieval},\text{role},\text{time},\text{help},\text{negative evidence})}
$$

## 8. Evidence-Confidence Gate

$$
\boxed{g=\sigma\left(w_g^\top x_{\text{confidence}}+b_g\right)}
$$

## 9. Fold-Safe Objective Prior

$$
\boxed{p_o=\frac{n_o^++\alpha p_{\text{global}}}{n_o+\alpha}}
$$

$$
\boxed{z_{\text{prior}}=\log\left(\frac{p_o}{1-p_o}\right)}
$$

## 10. Fusion

$$
\boxed{z_{\text{fusion}}=\beta_0+\beta_1z_{\text{prior}}+\beta_2gz_{\text{sem}}+\beta^\top x_{\text{struct}}}
$$

## 11. Neural Probability

$$
\boxed{p_N=\sigma(z_{\text{fusion}})}
$$

## 12. TF-IDF Logistic

$$
\boxed{p_T=\sigma\left(w_T^\top x_{\text{TFIDF}}+b_T\right)}
$$

## 13. OOF Blend

$$
\boxed{p_B=w^*p_N+(1-w^*)p_T}
$$

## 14. Optional Calibration

$$
\boxed{p_{\text{final}}=\operatorname{Calibrate}(p_B)}
$$

## Final

$$
\boxed{P(y=1\mid\text{Session},\text{Objective})=p_{\text{final}}}
$$

---

# PART 17 — Architecture আসলে কী শিখছে?

## ModernBERT

> Text meaning কী বলছে?

## BCE

> Individual prediction actual label-এর সাথে মিলাও।

## Pairwise Loss

> Same session-এর correct objective-কে incorrect objective-এর উপরে রাখো।

## Structured Feature Branch

> Evidence-এর shape কী? Student না tutor? Feedback-এর আগে/পরে কী হয়েছে?

## Evidence Gate

> Semantic evidence কতটা trust করা উচিত?

## Objective Prior

> Objective historically কতটা easy/hard?

## Fusion

> Semantic + evidence quality + objective difficulty একসাথে কী score দেয়?

## TF-IDF

> Stable lexical signal কী বলছে?

## OOF Blend

> Neural এবং sparse model-এর কোন mixture unseen data-তে best?

## Calibration

> Probability confidence বাস্তব frequency-এর সাথে aligned কি না?

---

# Final Architectural Insight

পুরো Step 11–26 এক লাইনে:

$$
\boxed{
\text{Semantic Understanding}
\rightarrow
\text{Individual + Pairwise Learning}
\rightarrow
\text{Evidence Reliability Correction}
\rightarrow
\text{Objective Difficulty Correction}
\rightarrow
\text{Neural Prediction}
\rightarrow
\text{Sparse Ensemble}
\rightarrow
\text{Calibrated Final Probability}
}
$$

মূল উদ্দেশ্য:

> শুধু overall session ভালো মনে হচ্ছে বলে সব objectives-কে কাছাকাছি positive probability না দেওয়া।

বরং:

$$
\boxed{
\text{Same Session}+\text{Different Objective Evidence}
\Rightarrow
\text{Different Final Probabilities}
}
$$

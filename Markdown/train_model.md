

```text
🏆 Gold Model
best_model_colab.pt
Validation LogLoss = 0.5465
Validation AUROC   = 0.7164
```

এটাই এখন থেকে আমাদের benchmark।

---

# 🎯 Challenge

আমাদের target:

```text
Input
↓
Tutoring Session
↓
Predict
↓
is_correct (0 / 1)
```

Evaluation metric:

> **LogLoss (Lower is Better)**

---

# 📍 আমরা এখন কোথায়?

| Model                |      LogLoss |
| -------------------- | -----------: |
| Word Logistic        | **0.545475** |
| Hybrid ModernBERT v1 |   **0.5465** |

এই result দেখে একটা জিনিস পরিষ্কার।

**Model weak না।**

বরং bottleneck অন্য জায়গায়।

---

# 🔍 এখন আমাদের hypothesis

আমরা blindly experiment করব না।

আমরা hypothesis-driven experiment করব।

---

## Hypothesis 1

❌ Positive word bias

Result:

> Dataset level-এ strong evidence পাইনি।

Reject.

---

## Hypothesis 2

🤔 Input representation weak

বর্তমানে text:

```text
Learning Objective

Tutor Text

Student Text
```

Question:

**এটাই কি best representation?**

---

## Hypothesis 3

🤔 Transcript structure better হতে পারে

কারণ

```text
Tutor

↓

Student

↓

Tutor

↓

Student
```

এই order হারিয়ে যাচ্ছে।

---

## Hypothesis 4

🤔 Model conversation-এর wrong অংশ ignore করছে।

এটা পরে Error Analysis দিয়ে দেখব।

---

# 🎯 Research Goal

আমরা model change করতে চাই না।

আমরা **signal improve করতে চাই।**

---

# 📈 Roadmap

## ✅ Phase 1 (Complete)

* Dataset merge
* Hybrid ModernBERT
* Baseline
* LogLoss = **0.5465**

শেষ।

---

## 🟡 Phase 2 (Current)

**Understand the problem**

আমরা এখন train করছি না।

আমরা বুঝব:

> Model-এর কাছে কী information যাচ্ছে?

---

### Task 1

বর্তমান input review

```
Learning Objective

Tutor Text

Student Text
```

---

### Task 2

Alternative input design

যেমন

```
Learning Objective

Transcript
```

অথবা

```
Learning Objective

Clean Transcript
```

---

### Task 3

Conversation cleaning

যেমন remove

```
[BACKGROUND]

[unclear]
```

---

## 🟢 Phase 3

ModernBERT v2

**শুধু একটা জিনিস change হবে।**

Text construction.

আর কিছু না।

---

## 🔵 Phase 4

Prediction export

```
validation_predictions.csv
```

---

## 🟣 Phase 5

Error Analysis

False Positive

False Negative

Hard examples

---

## 🔴 Phase 6

ModernBERT v3

Error analysis থেকে improvement।

---

# ❌ এখন কী করব না

* 2048 tokens
* ModernBERT Large
* DeBERTa
* Ensemble
* Hyperparameter tuning

এগুলো এখন নয়।

---

# 🎯 Success Criteria

আমাদের goal:

```
0.5465
    ↓
0.544
    ↓
0.542
    ↓
0.540
```

প্রতিটা improvement-এর কারণ জানতে হবে।

---
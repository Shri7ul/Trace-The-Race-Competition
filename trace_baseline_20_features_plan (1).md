# Trace the Ace — Baseline Transcript Feature Plan

## 1. Objective

এই stage-এ `train_transcripts/` folder-এর প্রতিটি transcript CSV থেকে একটি **session-level dataset** তৈরি করা হবে।

প্রতি session-এর জন্য আমরা:

1. কথোপকথন `utterance_id` অনুযায়ী সাজাব
2. `TUTOR`, `STUDENT`, `BACKGROUND` role আলাদা করব
3. tagged transcript তৈরি করব
4. ২০টি simple, fast ও explainable numerical feature তৈরি করব
5. প্রতি `session_id`-কে একটি row হিসেবে Parquet file-এ save করব

এই baseline stage-এ external dataset, LLM annotation, semantic classifier বা complex heuristic feature ব্যবহার করা হবে না।

---

## 2. Raw Transcript Columns

| Raw column | Meaning |
|---|---|
| `session_id` | Tutoring session-এর unique ID |
| `utterance_id` | Conversation turn-এর order |
| `role` | `tutor`, `student`, বা `background` |
| `content` | Spoken text |
| `timestamp` | Turn কখন ঘটেছে |

---

## 3. Output File

```text
outputs/
└── 01_transcript_merge/
    └── train_transcripts_baseline.parquet
```

প্রতি `session_id` একটি row হবে।

Numerical feature ছাড়াও নিচের columns রাখা হবে:

| Column | Purpose |
|---|---|
| `session_id` | `train_features.csv`-এর সঙ্গে merge key |
| `source_file` | Original transcript CSV name |
| `transcript_text` | Full conversation with role tags |
| `student_text` | শুধু student utterances |
| `tutor_text` | শুধু tutor utterances |

---

# 4. Final Refined 20 Features

## Group A — Session Size and Pace

### 1. `total_turns`

Session-এর মোট utterance সংখ্যা।

```text
total_turns = transcript CSV-এর মোট row
```

এটি session কত বড় এবং কত interaction হয়েছে তার basic signal।

---

### 2. `total_words`

সম্পূর্ণ transcript-এর মোট word সংখ্যা।

```text
total_words = প্রতিটি utterance-এর word count-এর যোগফল
```

উদাহরণ:

```text
"I think the answer is 12" → 6 words
```

এটি session-এর total verbal content বোঝায়।

---

### 3. `session_duration_minutes`

প্রথম valid timestamp এবং শেষ valid timestamp-এর পার্থক্য।

```text
session_duration_minutes =
(max timestamp − min timestamp) / 60
```

Valid timestamp না থাকলে `0.0`।

---

### 4. `turns_per_minute`

Conversation-এর pace।

```text
turns_per_minute =
total_turns / session_duration_minutes
```

Duration `0` হলে result `0.0`।

---

## Group B — Student and Tutor Participation

### 5. `student_turns`

```text
student_turns = count(role == "STUDENT")
```

Student কতবার কথা বলেছে।

---

### 6. `tutor_turns`

```text
tutor_turns = count(role == "TUTOR")
```

Tutor কতবার কথা বলেছে।

---

### 7. `student_turn_ratio`

```text
student_turn_ratio =
student_turns / total_turns
```

Range: `0.0–1.0`

এটি different session length-এর মধ্যে student participation compare করতে সাহায্য করে।

---

### 8. `student_word_ratio`

```text
student_word_ratio =
student_words / total_words
```

এটি student conversation-এর কত অংশ word volume হিসেবে contribute করেছে তা বোঝায়।

---

### 9. `avg_student_words_per_turn`

```text
avg_student_words_per_turn =
student_words / student_turns
```

Student short answer দিয়েছে নাকি longer response দিয়েছে তার rough signal।

---

### 10. `avg_tutor_words_per_turn`

```text
avg_tutor_words_per_turn =
tutor_words / tutor_turns
```

Tutor concise prompt দিয়েছে নাকি long explanation দিয়েছে তার rough signal।

---

## Group C — Student Response Style

### 11. `student_short_turn_ratio`

Student-এর কত শতাংশ response ৩টি word বা কম।

```text
student_short_turn_ratio =
count(student turns with word_count <= 3)
/
student_turns
```

Examples:

```text
"12"
"Yes"
"I don't know"
```

---

### 12. `student_long_turn_ratio`

Student-এর কত শতাংশ response ১০টি word বা বেশি।

```text
student_long_turn_ratio =
count(student turns with word_count >= 10)
/
student_turns
```

এটি extended response-এর rough signal। Long response মানেই correct reasoning নয়।

---

### 13. `student_numeric_turn_ratio`

Student-এর কত শতাংশ turn-এ অন্তত একটি digit আছে।

```text
student_numeric_turn_ratio =
count(student turns containing 0–9)
/
student_turns
```

Examples:

```text
"12"
"4 × 3 = 12"
"I think it is 24"
```

প্রথম baseline-এ number words যেমন `twelve` detect করা হবে না।

---

### 14. `student_question_ratio`

Student-এর কত শতাংশ turn-এ `?` আছে।

```text
student_question_ratio =
count(student turns containing "?")
/
student_turns
```

এটি clarification, confusion অথবা engagement-এর rough signal।

---

## Group D — Tutor Questioning and Response Flow

### 15. `tutor_question_ratio`

Tutor-এর কত শতাংশ turn question।

```text
tutor_question_ratio =
count(tutor turns containing "?")
/
tutor_turns
```

Raw count-এর বদলে ratio ব্যবহার করা হচ্ছে, যাতে long এবং short session তুলনা করা যায়।

---

### 16. `student_response_after_tutor_question_ratio`

Tutor question-এর পরের turn student-এর হয়েছে—এমন interaction-এর proportion।

```text
student_response_after_tutor_question_ratio =
count(
    previous turn = tutor question
    and current turn = student
)
/
tutor_question_turns
```

Example:

```text
[TUTOR] Why did you multiply?
[STUDENT] Because there are four groups.
```

Tutor question না থাকলে value `0.0`।

---

## Group E — Conversation Dynamics

### 17. `speaker_switch_rate`

Tutor ও student-এর মধ্যে speaker কত ঘন ঘন পরিবর্তন হয়েছে।

Background turns এখানে বাদ যাবে।

```text
speaker_switch_rate =
speaker changes
/
(tutor/student turns − 1)
```

Example:

```text
TUTOR → STUDENT → TUTOR → STUDENT
```

এটি highly interactive conversation নির্দেশ করতে পারে।

---

### 18. `longest_tutor_streak_ratio`

Tutor একটানা সর্বোচ্চ কয়টি turn বলেছে, সেটিকে tutor-এর মোট turn দিয়ে normalize করা।

```text
longest_tutor_streak_ratio =
longest consecutive tutor streak
/
tutor_turns
```

এটি tutor monologue dominance-এর rough signal।

---

### 19. `longest_student_streak_ratio`

Student একটানা সর্বোচ্চ কয়টি turn বলেছে, সেটিকে student-এর মোট turn দিয়ে normalize করা।

```text
longest_student_streak_ratio =
longest consecutive student streak
/
student_turns
```

এটি extended student participation-এর rough signal।

---

## Group F — Transcript Quality

### 20. `background_turn_ratio`

```text
background_turn_ratio =
background_turns / total_turns
```

Background/noise/setup content বেশি কি না বোঝায়।

Raw count-এর বদলে ratio রাখা হয়েছে, যাতে বিভিন্ন session length fairভাবে compare করা যায়।

---

# 5. Final Feature List

```text
01. total_turns
02. total_words
03. session_duration_minutes
04. turns_per_minute

05. student_turns
06. tutor_turns
07. student_turn_ratio
08. student_word_ratio
09. avg_student_words_per_turn
10. avg_tutor_words_per_turn

11. student_short_turn_ratio
12. student_long_turn_ratio
13. student_numeric_turn_ratio
14. student_question_ratio

15. tutor_question_ratio
16. student_response_after_tutor_question_ratio

17. speaker_switch_rate
18. longest_tutor_streak_ratio
19. longest_student_streak_ratio

20. background_turn_ratio
```

---

# 6. Why These Features Were Selected

এই set-এর selection principles:

- **Simple:** basic count, ratio এবং timestamp calculation
- **Fast:** heavy regex, embedding বা LLM call প্রয়োজন নেই
- **Explainable:** team member সহজে বুঝতে পারবে
- **Session-length aware:** raw count-এর সঙ্গে normalized ratio রাখা হয়েছে
- **Low-risk:** noisy rule-based educational labels বাদ রাখা হয়েছে
- **Compatible with text model:** পরে TF-IDF model-এর সঙ্গে ensemble করা যাবে

---

# 7. Features Deliberately Excluded

Initial baseline-এ নিচের features রাখা হবে না:

```text
student_reasoning_turns
student_uncertainty_turns
student_confidence_turns
student_self_correction_turns
tutor_hint_turns
tutor_explanation_turns
tutor_direct_answer_turns
positive_feedback_count
negative_feedback_count
first-vs-last progression
lexical diversity
semantic similarity
Bridge-style labels
TalkMoves labels
LLM-generated features
```

কারণ:

- phrase matching ভুল হতে পারে
- processing time বাড়ে
- baseline unnecessarily complex হয়
- validation improvement না দেখে complexity যোগ করা উচিত নয়

---

# 8. Data Cleaning Rules

## Role cleaning

```text
student    → STUDENT
tutor      → TUTOR
background → BACKGROUND
missing    → UNKNOWN
```

## Content cleaning

- Missing content → empty string
- Multiple spaces → single space
- Leading/trailing spaces removed

## Timestamp cleaning

- Valid timestamp → seconds
- Invalid timestamp → missing
- কোনো valid timestamp না থাকলে duration features `0.0`

## Safe division

সব ratio calculation-এ denominator `0` হলে result:

```text
0.0
```

---

# 9. Recommended Data Types

| Type | Suggested dtype |
|---|---|
| Counts | `int32` বা `int64` |
| Ratios | `float32` |
| Duration / pace | `float32` |
| IDs and text | `string` |

---

# 10. Baseline Modeling Plan

## Numerical Baseline

```text
20 numerical features
        ↓
Logistic Regression
        ↓
correctness probability
```

Optional comparison:

```text
20 numerical features
        ↓
CatBoost / LightGBM
```

## Text Baseline

```text
learning_objective
+
transcript_text
        ↓
Word TF-IDF + Character TF-IDF
        ↓
Logistic Regression
```

## Final Baseline Ensemble

```text
Numerical model probability
+
Word TF-IDF probability
+
Character TF-IDF probability
        ↓
Weighted average
```

---

# 11. Validation Rule

Random response-level split ব্যবহার করা হবে না।

```text
Group = session_id
```

একটি session-এর সব response একই split-এ থাকবে।

First validation:

```text
GroupShuffleSplit
80% sessions → train
20% sessions → validation
```

Later:

```text
5-fold GroupKFold
```

---

# 12. Final Data Flow

```text
train_transcripts/*.csv
        ↓
clean and order transcripts
        ↓
create transcript_text, student_text, tutor_text
        ↓
calculate 20 session-level features
        ↓
train_transcripts_baseline.parquet
        ↓
merge with train_features by session_id
        ↓
merge with train_labels by response_id
        ↓
master_train.parquet
        ↓
baseline training
```

---

# 13. Interpretation Warning

এই features learning-এর direct proof নয়।

- বেশি student words মানেই বেশি learning নয়
- বেশি tutor questions মানেই better tutoring নয়
- short answer মানেই weak understanding নয়
- long session মানেই effective session নয়

এগুলো measurable session signals।

কোন feature আসলে useful তা নির্ধারণ করবে validation score এবং Trace the Ace-এর training labels।

# Trace the Ace — EDA Findings and Feature Engineering Report

## 1. Purpose

This report converts the completed exploratory data analysis into a practical feature-engineering plan for the baseline modelling stage.

The following artifacts were reviewed:

- `1_eda.ipynb`
- `dataset_overview.csv`
- `target_summary.csv`
- `missing_summary.csv`
- `numerical_summary.csv`
- `outlier_summary.csv`
- `feature_target_correlation.csv`
- `correlation_matrix.csv`
- `high_correlation_pairs.csv`
- `band_target_summary.csv`
- `text_summary.csv`

The report separates **observed EDA evidence** from **recommended feature-engineering decisions**.

---

## 2. Executive Summary

The master dataset is clean and model-ready at the structural level:

- **35,072 response-level rows**
- **22,821 unique tutoring sessions**
- **36 columns**
- No duplicate `response_id`
- No fully duplicated rows
- No missing values recorded in the master table
- Target rate: **70.25% correct** and **29.75% incorrect**

The major modelling implications are:

1. The same `session_id` appears in multiple response rows, so validation must be grouped by `session_id`.
2. Individual numerical transcript features have weak linear relationships with correctness. The largest absolute session-level correlation is below `0.09`.
3. Student response-depth features are the most promising structured signals.
4. Total conversation volume is comparatively weak.
5. Several numerical features are highly redundant, especially turn counts and response-length measures.
6. Some ratio and streak features are strongly skewed and contain IQR outliers, but rows should not be deleted.
7. Full transcripts are long, averaging about **3,914 words**, so TF-IDF is suitable for the baseline while transformer models would require truncation or chunking.
8. The current LOW/MEDIUM/HIGH bands were created before the validation split. They are useful for EDA, but their thresholds must be fitted again using only the training split before leakage-safe validation.

---

## 3. Dataset Structure

| Metric                 | Value   |
|:-----------------------|:--------|
| Total rows             | 35,072  |
| Total columns          | 36      |
| Unique response IDs    | 35,072  |
| Unique session IDs     | 22,821  |
| Repeated session rows  | 12,251  |
| Duplicate response IDs | 0       |
| Fully duplicated rows  | 0       |

### Interpretation

- Every row represents an assessment response.
- `response_id` is the response-level unique key.
- `session_id` is expected to repeat because one tutoring session can produce several assessment responses.
- The **12,251 repeated session rows are valid**, not duplicate errors.
- Transcript-derived features are session-level values repeated across all responses belonging to the same session.

---

## 4. Target Distribution

|   label | meaning   | count   | percentage   |
|--------:|:----------|:--------|:-------------|
|       0 | Incorrect | 10,435  | 29.75%       |
|       1 | Correct   | 24,637  | 70.25%       |

The training positive rate is **70.25%**.

A constant-probability dummy model that predicts `0.7025` for every row would have an expected log loss of approximately **0.6088**. This should be used as the minimum reference for baseline models.

### Modelling implication

The target is moderately imbalanced, but not extremely imbalanced. For probability-focused evaluation:

- Do not automatically use `class_weight="balanced"`.
- Compare class weighting only as an experiment because it can harm probability calibration and log loss.
- Use log loss as the main metric and ROC-AUC/accuracy as secondary metrics.

---

## 5. Data Quality Findings

The saved missing-value report contains **zero missing values in all 36 columns**.

Additional observations:

- `student_text` contains **5 empty strings**, although they are not stored as missing values.
- Numerical features contain no reported missing values.
- No duplicate response IDs or full duplicate rows were found.
- Empty text values should be converted to `""` consistently before text vectorization.
- Infinite values should still be replaced inside the model pipeline as a defensive step.

---

## 6. Session and Response Structure

The EDA notebook reported:

- Mean responses per session: **1.5368**
- Median responses per session: **1**
- 75th percentile: **2**
- Maximum responses in one session: **10**

Session-level outcome patterns:

| Session outcome pattern | Session count | Percentage |
|---|---:|---:|
| All responses correct | 13,582 | 59.52% |
| All responses incorrect | 6,032 | 26.43% |
| Mixed correct and incorrect | 3,207 | 14.05% |

### Interpretation

Most sessions contain only one response. Therefore:

- Session correct rates are often exactly `0` or `1`.
- Session-level correlations are useful for exploration but can be unstable for sessions with one response.
- The actual competition model should remain response-level.
- All responses from one session must stay in the same train or validation partition.
- Optional later experiments may weight each response by `1 / responses_in_session`, but the first baseline should use ordinary response-level training.

---

## 7. Numerical Feature Summary

The following statistics were calculated with one row per unique session.

| Feature                                     | Mean       | Median     | Q1         | Q3         |     Min | Max        | Zero %   |   Skewness |
|:--------------------------------------------|:-----------|:-----------|:-----------|:-----------|--------:|:-----------|:---------|-----------:|
| total_turns                                 | 269.0440   | 267.0000   | 222.0000   | 316.0000   | 15.0000 | 622.0000   | 0.000%   |     0.0865 |
| total_words                                 | 3,644.9225 | 3,681.0000 | 3,045.0000 | 4,270.0000 | 39.0000 | 8,663.0000 | 0.000%   |    -0.1963 |
| session_duration_minutes                    | 41.4253    | 43.3833    | 39.1833    | 45.0833    |  3.4167 | 62.0167    | 0.000%   |    -1.9590 |
| turns_per_minute                            | 6.4922     | 6.4455     | 5.4947     | 7.4529     |  0.5749 | 13.4278    | 0.000%   |     0.1306 |
| student_turns                               | 118.1873   | 118.0000   | 94.0000    | 142.0000   |  0.0000 | 295.0000   | 0.022%   |     0.0937 |
| tutor_turns                                 | 140.0465   | 139.0000   | 117.0000   | 163.0000   |  4.0000 | 559.0000   | 0.000%   |     0.1186 |
| student_turn_ratio                          | 0.4352     | 0.4455     | 0.4100     | 0.4728     |  0.0000 | 0.8101     | 0.022%   |    -1.5147 |
| student_word_ratio                          | 0.2681     | 0.2625     | 0.2027     | 0.3274     |  0.0000 | 0.8679     | 0.022%   |     0.4618 |
| avg_student_words_per_turn                  | 8.3661     | 7.8824     | 6.2931     | 9.9000     |  0.0000 | 38.6471    | 0.022%   |     1.2449 |
| avg_tutor_words_per_turn                    | 18.7152    | 17.9563    | 15.0861    | 21.5145    |  1.2000 | 65.5614    | 0.000%   |     1.0639 |
| student_short_turn_ratio                    | 0.5079     | 0.5049     | 0.4238     | 0.5888     |  0.0000 | 1.0000     | 0.026%   |     0.1347 |
| student_long_turn_ratio                     | 0.2558     | 0.2478     | 0.1867     | 0.3158     |  0.0000 | 0.7500     | 0.167%   |     0.4595 |
| student_numeric_turn_ratio                  | 0.3491     | 0.3462     | 0.2692     | 0.4286     |  0.0000 | 1.0000     | 0.245%   |     0.0929 |
| student_question_ratio                      | 0.1598     | 0.1497     | 0.1102     | 0.1986     |  0.0000 | 0.9167     | 0.202%   |     1.0551 |
| tutor_question_ratio                        | 0.6242     | 0.6338     | 0.5400     | 0.7168     |  0.0000 | 1.0000     | 0.013%   |    -0.4050 |
| student_response_after_tutor_question_ratio | 0.7735     | 0.7976     | 0.7143     | 0.8603     |  0.0000 | 1.0000     | 0.066%   |    -1.5328 |
| speaker_switch_rate                         | 0.7904     | 0.8075     | 0.7591     | 0.8438     |  0.0000 | 0.9762     | 0.022%   |    -2.3985 |
| longest_tutor_streak_ratio                  | 0.0405     | 0.0326     | 0.0242     | 0.0458     |  0.0078 | 1.0000     | 0.000%   |     9.7130 |
| longest_student_streak_ratio                | 0.0317     | 0.0263     | 0.0200     | 0.0360     |  0.0000 | 1.0000     | 0.022%   |    10.0256 |
| background_turn_ratio                       | 0.0395     | 0.0317     | 0.0190     | 0.0514     |  0.0000 | 0.7031     | 0.684%   |     2.6775 |

### Main distribution findings

- Typical sessions contain around **267 turns** and **3,681 words**.
- Median session duration is **43.38 minutes**.
- Students produce about **44.55% of turns** but only **26.25% of words** at the median.
- Median student response length is **7.88 words per turn**.
- Median tutor response length is **17.96 words per turn**.
- About half of student turns are short: median `student_short_turn_ratio = 0.5049`.
- Tutors ask questions frequently: median `tutor_question_ratio = 0.6338`.
- Student responses follow tutor questions frequently: median ratio `0.7976`.
- Speaker switching is high: median `speaker_switch_rate = 0.8075`.
- Background turns are generally limited: median `background_turn_ratio = 0.0317`.

---

## 8. Feature Relationships with Session Correctness

All correlations are weak in absolute terms. This means no individual structured feature is sufficient by itself.

| Feature                                     |   Correlation with session correct rate |
|:--------------------------------------------|----------------------------------------:|
| student_long_turn_ratio                     |                                  0.0877 |
| avg_student_words_per_turn                  |                                  0.0801 |
| student_word_ratio                          |                                  0.0548 |
| student_response_after_tutor_question_ratio |                                  0.0407 |
| total_words                                 |                                  0.0293 |
| student_turn_ratio                          |                                  0.0238 |
| avg_tutor_words_per_turn                    |                                  0.0213 |
| speaker_switch_rate                         |                                  0.0147 |
| session_duration_minutes                    |                                  0.0023 |
| background_turn_ratio                       |                                  0.0010 |
| longest_student_streak_ratio                |                                 -0.0015 |
| student_turns                               |                                 -0.0045 |
| longest_tutor_streak_ratio                  |                                 -0.0045 |
| student_numeric_turn_ratio                  |                                 -0.0149 |
| total_turns                                 |                                 -0.0153 |
| turns_per_minute                            |                                 -0.0194 |
| tutor_question_ratio                        |                                 -0.0239 |
| tutor_turns                                 |                                 -0.0250 |
| student_question_ratio                      |                                 -0.0297 |
| student_short_turn_ratio                    |                                 -0.0569 |

### Strongest observed signals

Positive:

- `student_long_turn_ratio`: `0.0877`
- `avg_student_words_per_turn`: `0.0801`
- `student_word_ratio`: `0.0548`
- `student_response_after_tutor_question_ratio`: `0.0407`
- `total_words`: `0.0293`

Negative:

- `student_short_turn_ratio`: `-0.0569`
- `student_question_ratio`: `-0.0297`
- `tutor_turns`: `-0.0250`
- `tutor_question_ratio`: `-0.0239`
- `turns_per_minute`: `-0.0194`

### Interpretation

The structured EDA consistently suggests that **student response depth and contribution are more useful than raw session volume**.

However, the maximum absolute correlation is below `0.09`, so:

- Structured features should be treated as supporting signals.
- Text features are likely to provide more predictive information.
- Nonlinear relationships may exist even when Pearson correlation is weak.
- These results show association, not causation.

---

## 9. Threshold-Band Findings

| Band feature                 |   LOW correct rate |   MEDIUM correct rate |   HIGH correct rate |   HIGH − LOW | LOW responses   | MEDIUM responses   | HIGH responses   |
|:-----------------------------|-------------------:|----------------------:|--------------------:|-------------:|:----------------|:-------------------|:-----------------|
| dialogue_switch_band         |             0.6963 |                0.7056 |              0.7060 |       0.0097 | 12,261          | 11,804             | 11,007           |
| session_duration_band        |             0.6944 |                0.7023 |              0.7096 |       0.0152 | 10,656          | 12,195             | 12,221           |
| session_turn_volume_band     |             0.7058 |                0.7093 |              0.6917 |      -0.0141 | 11,811          | 12,012             | 11,249           |
| student_response_length_band |             0.6587 |                0.6963 |              0.7437 |       0.0850 | 10,513          | 11,653             | 12,906           |
| student_short_turn_band      |             0.7278 |                0.7019 |              0.6721 |      -0.0557 | 12,921          | 11,588             | 10,563           |
| student_turn_share_band      |             0.6899 |                0.7061 |              0.7114 |       0.0216 | 11,744          | 11,559             | 11,769           |
| tutor_questioning_band       |             0.7134 |                0.7015 |              0.6900 |      -0.0234 | 12,975          | 11,663             | 10,434           |

### Main conclusions

- `student_response_length_band` has the clearest separation: `0.6587 → 0.7437`.
- `student_short_turn_band` moves in the opposite direction: `0.7278 → 0.6721`.
- `student_turn_share_band` shows a mild positive trend.
- `session_duration_band` shows a small positive pattern even though the raw duration correlation is almost zero. This suggests a weak nonlinear effect.
- `tutor_questioning_band` shows a mild negative pattern.
- `dialogue_switch_band` shows only a small difference.
- `session_turn_volume_band` is weak and non-monotonic. The notebook explicitly notes that this band can be removed.

### Leakage warning

The existing bands were derived from the full dataset. For valid train-validation evaluation:

1. Split by `session_id`.
2. Calculate Q33/Q67 thresholds using the training partition only.
3. Save those threshold values.
4. Apply the saved values to validation and later test data.
5. Never recalculate thresholds independently on validation or test data.

---

## 10. High-Correlation and Redundancy Findings

The following feature pairs have absolute correlation of at least `0.85`.

| Feature 1                                   | Feature 2                                   |   Correlation |
|:--------------------------------------------|:--------------------------------------------|--------------:|
| total_turns                                 | tutor_turns                                 |        0.9578 |
| total_turns                                 | student_turns                               |        0.9293 |
| avg_student_words_per_turn                  | student_long_turn_ratio                     |        0.9022 |
| total_turns                                 | turns_per_minute                            |        0.8641 |
| student_response_after_tutor_question_ratio | speaker_switch_rate                         |        0.8576 |
| student_turn_ratio                          | student_response_after_tutor_question_ratio |        0.8553 |

### Implications

- `total_turns`, `student_turns`, and `tutor_turns` contain overlapping conversation-volume information.
- `avg_student_words_per_turn` and `student_long_turn_ratio` capture nearly the same response-depth pattern.
- `total_turns` and `turns_per_minute` overlap strongly.
- `student_response_after_tutor_question_ratio`, `speaker_switch_rate`, and `student_turn_ratio` contain overlapping interaction information.

### Recommended strategy

For the first baseline:

- Keep all 20 numerical features.
- Use L2-regularized logistic regression.
- Do not remove features before obtaining a reproducible baseline score.

Then run an ablation experiment:

- Full 20 numerical features
- Reduced feature set with one representative from each highly correlated group

This is safer than deleting features based only on correlation.

---

## 11. Skewness and IQR Outliers

No rows should be deleted solely because they are IQR outliers.

| Feature                                     |   Skewness | IQR lower limit   | IQR upper limit   | Outlier count   | Outlier percentage   |
|:--------------------------------------------|-----------:|:------------------|:------------------|:----------------|:---------------------|
| longest_tutor_streak_ratio                  |     9.7130 | -0.0081           | 0.0781            | 1,437           | 6.297%               |
| longest_student_streak_ratio                |    10.0256 | -0.0041           | 0.0601            | 1,383           | 6.060%               |
| session_duration_minutes                    |    -1.9590 | 30.3333           | 53.9333           | 1,113           | 4.877%               |
| speaker_switch_rate                         |    -2.3985 | 0.6321            | 0.9707            | 1,036           | 4.540%               |
| background_turn_ratio                       |     2.6775 | -0.0297           | 0.1000            | 1,022           | 4.478%               |
| student_turn_ratio                          |    -1.5147 | 0.3157            | 0.5670            | 964             | 4.224%               |
| student_response_after_tutor_question_ratio |    -1.5328 | 0.4953            | 1.0793            | 778             | 3.409%               |
| avg_tutor_words_per_turn                    |     1.0639 | 5.4435            | 31.1571           | 655             | 2.870%               |
| avg_student_words_per_turn                  |     1.2449 | 0.8828            | 15.3103           | 655             | 2.870%               |
| student_question_ratio                      |     1.0551 | -0.0224           | 0.3312            | 472             | 2.068%               |
| turns_per_minute                            |     0.1306 | 2.5572            | 10.3904           | 392             | 1.718%               |
| tutor_turns                                 |     0.1186 | 48.0000           | 232.0000          | 366             | 1.604%               |
| student_turns                               |     0.0937 | 22.0000           | 214.0000          | 354             | 1.551%               |
| total_turns                                 |     0.0865 | 81.0000           | 457.0000          | 337             | 1.477%               |
| total_words                                 |    -0.1963 | 1,207.5000        | 6,107.5000        | 328             | 1.437%               |
| student_word_ratio                          |     0.4618 | 0.0158            | 0.5143            | 253             | 1.109%               |
| student_long_turn_ratio                     |     0.4595 | -0.0070           | 0.5095            | 236             | 1.034%               |
| tutor_question_ratio                        |    -0.4050 | 0.2748            | 0.9820            | 146             | 0.640%               |
| student_numeric_turn_ratio                  |     0.0929 | 0.0302            | 0.6676            | 131             | 0.574%               |
| student_short_turn_ratio                    |     0.1347 | 0.1764            | 0.8362            | 104             | 0.456%               |

### Main risks

- `longest_tutor_streak_ratio` and `longest_student_streak_ratio` are extremely right-skewed.
- `background_turn_ratio` has a long right tail.
- `speaker_switch_rate` and `student_response_after_tutor_question_ratio` are concentrated near the upper boundary.
- `session_duration_minutes` is negatively skewed and has both short- and long-session extremes.
- Average student and tutor word counts have moderate right tails.

### Basic treatment

For the first baseline:

- Replace infinite values with missing.
- Median-impute defensively.
- Use `StandardScaler` for logistic regression.
- Do not delete outlier rows.

For a second structured experiment:

- Clip selected features using **training-only** 1st and 99th percentiles.
- Add `log1p` copies for strongly right-skewed non-negative features.
- Compare `RobustScaler` against `StandardScaler`.

Possible transformed features:

- `log_avg_student_words_per_turn`
- `log_avg_tutor_words_per_turn`
- `log_longest_tutor_streak_ratio`
- `log_longest_student_streak_ratio`
- `log_background_turn_ratio`

`session_duration_minutes` should be clipped rather than logged because its skewness is negative.

---

## 12. Text-Length Findings

| Text column        |   Empty count | Mean characters   | Median characters   | Maximum characters   | Mean words   | Median words   | Maximum words   |
|:-------------------|--------------:|:------------------|:--------------------|:---------------------|:-------------|:---------------|:----------------|
| learning_objective |             0 | 42.47             | 39.00               | 83.00                | 6.56         | 6.00           | 15.00           |
| transcript_text    |             0 | 20,958.81         | 21,186.00           | 49,333.00            | 3,913.97     | 3,957.00       | 9,134.00        |
| student_text       |             5 | 4,871.07          | 4,688.00            | 16,207.00            | 974.98       | 934.00         | 3,385.00        |
| tutor_text         |             0 | 13,063.73         | 12,992.00           | 33,781.00            | 2,558.13     | 2,543.00       | 6,453.00        |

### Interpretation

- Learning objectives are short, with a median of **6 words**.
- Full transcripts are very long, with a median of **3,957 words** and a maximum of **9,134 words**.
- Student text has a median of **934 words**.
- Tutor text has a median of **2,543 words**.
- Tutor content is substantially longer than student content.
- Student contribution increases with total transcript length, but text volume alone does not separate correct from incorrect outcomes.
- Some long sessions remain tutor-dominated, which supports keeping contribution ratios such as `student_word_ratio`.

### Text feature recommendation

Create:

```text
[OBJECTIVE] <learning_objective>
[TRANSCRIPT] <transcript_text>
```

as the main `model_text`.

Baseline text experiments:

1. Word TF-IDF on `model_text`
2. Character TF-IDF on `model_text`
3. Optional student-focused TF-IDF using objective + `student_text`
4. Optional tutor-focused TF-IDF using objective + `tutor_text`

The first model should use the full tagged transcript. Student-only and tutor-only variants are ablation experiments.

---

## 13. Final Feature-Engineering Plan

### 13.1 Columns not used as predictive inputs

- `response_id`: identifier only
- `session_id`: grouping key only
- `source_file`: file-system artifact
- `correct`: target

`learning_objective_id` should be treated cautiously. It may be useful as a categorical feature, but it should be tested separately because objective IDs can act as high-cardinality identifiers.

### 13.2 Numerical feature set

Start with all 20 original numerical features.

Baseline processing:

```text
replace ±inf → NaN
median imputation
StandardScaler
L2 Logistic Regression
```

Second experiment:

```text
training-only clipping
selected log1p features
RobustScaler
L2 Logistic Regression
```

### 13.3 Threshold categorical features

Recommended baseline categorical set:

- `session_duration_band`
- `student_turn_share_band`
- `student_response_length_band`
- `student_short_turn_band`
- `tutor_questioning_band`
- `dialogue_switch_band`

Remove from the main feature set:

- `session_turn_volume_band`

Reason: it is weak, non-monotonic, and duplicates information already present in `total_turns`.

Use one-hot encoding with unknown-category handling.

### 13.4 Text features

Create `model_text` by combining:

- Learning objective
- Full tagged transcript

Use:

- Word TF-IDF: `(1, 2)` word n-grams
- Character TF-IDF: `char_wb`, approximately `(3, 5)` n-grams
- Logistic regression for both

### 13.5 Missing and empty values

- Fill missing text with `""`.
- The 5 empty `student_text` sessions should remain valid rows.
- Fit numerical imputers only on the training split.
- Do not use validation statistics during preprocessing.

### 13.6 Validation split

Required rule:

```text
Group = session_id
```

Basic split:

```text
80% unique sessions → train
20% unique sessions → validation
```

Validation requirements:

- No shared `session_id` between partitions
- Similar target distribution in both partitions
- All thresholds, imputers, scalers, and vectorizers fitted on training data only

Later, use `StratifiedGroupKFold` or `GroupKFold` for more stable evaluation.

---

## 14. Recommended Baseline Experiments

| Experiment | Input | Purpose |
|---|---|---|
| Dummy probability | Training target mean | Minimum reference |
| Structured A | 20 raw numerical features | Establish structured baseline |
| Structured B | 20 numerical + 6 categorical bands | Test threshold nonlinearity |
| Structured C | Transformed numerical + 6 bands | Test skew/outlier treatment |
| Text A | Word TF-IDF on `model_text` | Main text baseline |
| Text B | Character TF-IDF on `model_text` | Capture spelling, equations, and local patterns |
| Ensemble | Structured + word + character probabilities | Improve log loss through complementary signals |

Model selection should use validation log loss.

---

## 15. Suggested Feature-Engineering Notebook Outputs

```text
Trace-The-Race-Dataset/
└── outputs/
    └── 05_feature_engineering/
        ├── train_engineered.parquet
        ├── validation_engineered.parquet
        ├── train_session_ids.csv
        ├── validation_session_ids.csv
        ├── fitted_band_thresholds.json
        ├── feature_config.json
        └── feature_engineering_summary.md
```

`feature_config.json` should record:

- ID columns
- Target column
- Numerical columns
- Categorical columns
- Text column
- Dropped columns
- Random seed
- Split method
- Train-derived threshold values

---

## 16. Final Decisions

1. Keep the response-level master table.
2. Split by `session_id`, never randomly by response.
3. Keep all 20 numerical features for the first baseline.
4. Remove `session_turn_volume_band` from the main categorical set.
5. Refit all band thresholds using training sessions only.
6. Use 6 remaining bands as an optional structured experiment.
7. Do not delete outlier rows.
8. Start with simple imputation and scaling.
9. Add selected transformed features only as a comparison.
10. Build objective + transcript text for TF-IDF.
11. Use log loss as the main metric.
12. Treat the constant-probability log loss of about **0.6088** as the minimum benchmark.
13. Compare full and reduced structured feature sets through grouped validation rather than correlation-based deletion alone.

---

## 17. Main Limitation

Most sessions contain only one assessment response. As a result, session-level correctness is frequently `0` or `1`, and session-level correlations can be noisy.

The primary training and evaluation unit should therefore remain the **assessment response**, while session grouping is used to prevent leakage.

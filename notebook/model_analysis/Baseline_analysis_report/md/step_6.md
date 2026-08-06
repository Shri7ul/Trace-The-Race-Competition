আমি `06_group_analysis.zip`-এর core summary tables, fold-stability files, audit/manifest, Step 5 linkage, intersection results এবং final synthesis charts cross-check করেছি।

## সবচেয়ে গুরুত্বপূর্ণ সারসংক্ষেপ

এই baseline-এর মূল সমস্যা **overall Log Loss বা accuracy কম হওয়া নয়**। মূল সমস্যা হলো:

> **Model অত্যন্ত বেশি “positive/correct” predict করছে এবং একই session-এর correct objective ও incorrect objective আলাদা করতে পারছে না।**

এ কারণে সাধারণ accuracy দেখে model মোটামুটি ভালো মনে হয়, কিন্তু negative responses এবং mixed-label sessions-এ performance খুব দুর্বল।

---

# 1. Overall baseline কী বলছে?

Dataset:

| বিষয়                                |      ফলাফল |
| ----------------------------------- | ---------: |
| Responses                           |     35,072 |
| Sessions                            |     22,821 |
| Learning objectives                 |        396 |
| Positive response rate              |     70.25% |
| Mean predicted probability          |     70.42% |
| Log Loss                            |     0.5555 |
| AUROC                               |     0.7007 |
| Raw accuracy                        |     72.18% |
| **Balanced accuracy**               | **56.84%** |
| Positive-class Log Loss             |     0.3270 |
| **Negative-class Log Loss**         | **1.0950** |
| **False-positive rate**             | **81.04%** |
| False-negative rate                 |      5.28% |
| High-confidence false-positive rate |     13.26% |

প্রথম দেখায় 72.18% accuracy ভালো মনে হতে পারে। কিন্তু balanced accuracy মাত্র 56.84%। কারণ model positive responses প্রায় সব ধরছে, কিন্তু negative responses-এর মাত্র 18.96% সঠিকভাবে negative হিসেবে ধরছে।

সহজভাবে:

```text
Positive response এলে → Model বেশিরভাগ সময় ঠিক
Negative response এলে → Model প্রায় 81% ক্ষেত্রে ভুল করে positive বলে
```

এই pattern পাঁচটি fold-এই stable:

```text
Fold-wise FPR: প্রায় 79.4%–82.3%
Fold-wise negative LL: প্রায় 1.08–1.12
```

অর্থাৎ এটি কোনো একটি fold-এর accident নয়; এটি model-এর systematic behaviour।
[Overall reference](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/00_reference/overall_reference.csv) · [Fold reference](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/00_reference/fold_reference.csv)

---

# 2. Global calibration দেখতে ভালো, কিন্তু আসলে misleading

Global positive prevalence 70.25% এবং mean probability 70.42%—দুটি প্রায় সমান।

এটি দেখে মনে হতে পারে model calibrated। কিন্তু বাস্তব সমস্যা হলো:

* All-positive sessions-এ model ভালো;
* All-negative ও mixed-label sessions-এও model অনেক বেশি positive probability দেয়;
* ভিন্ন group-এর ভুলগুলো global average-এ cancel হয়ে যাচ্ছে।

বিশেষ করে:

| Session type | Actual positive rate | Mean probability |  Log Loss |        FPR |
| ------------ | -------------------: | ---------------: | --------: | ---------: |
| All-negative |                   0% |       **59.74%** | **0.976** | **74.89%** |
| All-positive |                 100% |           73.54% |     0.325 |          — |
| Mixed-label  |               55.58% |       **71.56%** | **0.770** | **92.32%** |

All-negative session-এ কোনো positive label নেই, তারপরও average probability প্রায় 60%। এটি খুব পরিষ্কার positive-bias evidence।

Mixed-label sessions-এ actual positive rate 55.58%, কিন্তু model average 71.56% probability দিয়েছে—প্রায় **16 percentage point overprediction**।

আরও গুরুত্বপূর্ণ:

```text
Mixed-label balanced accuracy = 51.15%
Mixed-label negative LL = 1.313
Mixed-label high-confidence FP rate = 24.83%
```

অর্থাৎ mixed-label population-এ model প্রায় chance-level balanced discrimination করছে।
[Label-structure summary](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/session_complexity/label_structure_summary.csv) · [Headline registry](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/class_conditional_prevalence/headline_group_registry.csv)

---

# 3. একই session-এ objectives বাড়লে সবচেয়ে বড় problem দেখা যাচ্ছে

এটি research-এর সবচেয়ে গুরুত্বপূর্ণ findings-এর একটি।

Overall Log Loss দেখলে মনে হচ্ছে বেশি objectives থাকা sessions ভালো:

| Objectives/session | Overall LL | Negative LL |        FPR | High-confidence FP |
| ------------------ | ---------: | ----------: | ---------: | -----------------: |
| 1                  |      0.603 |       0.950 |     73.04% |              5.74% |
| 2                  |      0.546 |       1.165 |     86.80% |             15.77% |
| 3–4                |      0.497 |       1.336 |     93.34% |             26.01% |
| **5+**             |  **0.473** |   **1.716** | **98.33%** |         **57.74%** |

এখানে apparent contradiction আছে:

```text
Objectives বাড়ছে → Overall LL কমছে
কিন্তু
Objectives বাড়ছে → Negative LL ও FPR ভয়াবহভাবে বাড়ছে
```

কারণ objectives বেশি থাকা sessions-এ positive label rate-ও বেশি। Model সবকিছুকে positive বললে positive rows-এর কারণে overall score ভালো দেখায়, কিন্তু incorrect objectives প্রায় সব ভুল হয়।

বিশেষ করে 5+ objective group:

* FPR 98.33%;
* অর্থাৎ প্রায় প্রতিটি negative objective-কে positive বলা হয়েছে;
* negative LL 1.716;
* 57.74% negative response-এ probability 0.80 বা তারও বেশি;
* balanced accuracy মাত্র 50.79%।

তাই “5+ objective sessions model-এর জন্য সহজ”—এটি সম্পূর্ণ ভুল conclusion হবে।

সঠিক conclusion:

> **Larger multi-objective sessions-এ overall metric label prevalence দ্বারা masked হচ্ছে; model incorrect objectives আলাদা করতে পারছে না।**

[Session-complexity summary](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/session_complexity/objectives_per_session_summary.csv)

---

# 4. Step 5 linkage সরাসরি objective collapse confirm করেছে

Step 5-এর 3,207 mixed-label sessions-এর সবগুলোই Step 6-এর সঙ্গে successfully merge হয়েছে—coverage 100%।

Overall mixed-session mechanism:

| Metric                        |      ফলাফল |
| ----------------------------- | ---------: |
| Mean session margin           | **0.0085** |
| Session pairwise accuracy     |     67.60% |
| **Session collapse rate**     | **74.93%** |
| Session reversal rate         |     31.28% |
| Mean collapsed-pair share     |     72.56% |
| Negative-objective loss       |      1.307 |
| Mean max-negative probability |      0.702 |

Session margin:

[
\text{mean correct probability}
-------------------------------

\text{mean incorrect probability}
]

Mean margin মাত্র 0.0085। অর্থাৎ correct objective এবং incorrect objective-এর probability প্রায় একই।

প্রায় 75% mixed session collapse threshold-এর মধ্যে আছে।

আর 5+ objective mixed sessions-এ:

```text
Session collapse rate = 88.71%
Negative-objective loss = 1.823
Mean max-negative probability = 0.813
```

অর্থাৎ incorrect objective-কে model average 81% পর্যন্ত maximum probability দিচ্ছে।

এটি আমাদের মূল hypothesis confirm করে:

> **Model transcript-এর general positive/mastery signal ধরছে, কিন্তু objective-specific evidence আলাদা করতে পারছে না।**

[Step 5 linkage](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/step5_linkage/mixed_session_group_linkage.csv) · [Merge audit](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/step5_linkage/step5_linkage_merge_audit.csv)

---

# 5. Rare এবং unseen objectives-এ generalization problem আছে

Objective support analysis:

| Support group  | Responses | Log Loss | Negative LL |      FPR | AUROC |
| -------------- | --------: | -------: | ----------: | -------: | ----: |
| Unseen         |        83 |    0.677 |       1.252 | **100%** | 0.511 |
| Very rare      |       650 |    0.575 |       1.251 |   92.27% | 0.608 |
| Rare           |     2,315 |    0.610 |       1.056 |   85.05% | 0.656 |
| Medium support |     9,142 |    0.572 |       1.053 |   78.60% | 0.694 |
| Common         |    22,882 |    0.542 |       1.113 |   81.24% | 0.708 |

Important interpretation:

* Unseen group খুব খারাপ, কিন্তু মাত্র 83 responses—এটি headline conclusion-এর জন্য যথেষ্ট support নয়।
* Very rare এবং rare groups fold-stable high-risk।
* বেশি support overall performance improve করে।
* কিন্তু common objectives-এও FPR 81.24% এবং negative LL 1.113।

অর্থাৎ:

> **Objective support problem আছে, কিন্তু বেশি training support দিলেই false-positive problem পুরো solve হচ্ছে না।**

আর objective-macro evaluation response-weighted score-এর চেয়ে খারাপ:

| Evaluation        |  Log Loss |     AUROC |        FPR |
| ----------------- | --------: | --------: | ---------: |
| Response-weighted |     0.555 |     0.701 |     81.04% |
| Objective-macro   | **0.594** | **0.590** | **90.58%** |

এর মানে common objectives-এর অনেক responses overall metric-কে dominate করছে। অনেক individual objective-তে performance average score-এর চেয়ে খারাপ।

[Objective-support summary](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/objective_frequency/objective_support_group_summary.csv) · [Objective-macro scorecard](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/objective_frequency/objective_macro_scorecard.csv) · [Worst supported objectives](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/objective_frequency/worst_supported_objectives.csv)

---

# 6. Transcript length-এর ফলাফল প্রথম দেখায় উল্টো মনে হয়

Overall Log Loss:

| Transcript | Overall LL | Positive LL | Negative LL |        FPR |
| ---------- | ---------: | ----------: | ----------: | ---------: |
| Short      |  **0.574** |       0.351 |       1.068 |     79.79% |
| Medium     |      0.561 |       0.327 |       1.087 |     81.07% |
| Long       |      0.550 |       0.327 |       1.089 |     79.90% |
| Very long  |  **0.536** |       0.303 |   **1.141** | **83.66%** |

Short transcript overall সবচেয়ে খারাপ এবং পাঁচ fold-এই stable high-risk।

কিন্তু transcript বড় হওয়ার সঙ্গে:

```text
Overall LL কমছে
Positive LL কমছে
Negative LL বাড়ছে
FPR বাড়ছে
```

Continuous analysis-ও একই result দেখিয়েছে:

```text
Total words বনাম overall loss:
rho = -0.068
95% CI = [-0.080, -0.054]
```

কিন্তু largest bins-এ negative LL প্রায় 1.17 পর্যন্ত উঠেছে।

তাই conclusion হবে না:

> Longer transcripts improve the model.

সঠিক conclusion:

> Longer transcripts-এ positive evidence বেশি পাওয়া যাচ্ছে, তাই overall loss কমছে; কিন্তু incorrect objective rejection আরও খারাপ হচ্ছে।

অতএব naive truncation solution নয়। দরকার **objective-relevant turn selection**।

[Transcript-length summary](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/transcript_length/transcript_length_summary.csv) · [Continuous trends](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/continuous_trends/continuous_spearman_summary.csv)

---

# 7. Student–tutor behaviour কী বলছে?

কিছু stable patterns পাওয়া গেছে:

* Lowest student-word-share group overall LL 0.574;
* Low average student words per turn LL 0.586;
* Low student long-turn ratio LL 0.587;
* Very high student short-turn ratio LL 0.579;
* Low response-after-tutor-question ratio LL 0.576।

এগুলো দেখায় student evidence অল্প বা fragmented হলে positive examples চিনতে model কষ্ট পাচ্ছে।

কিন্তু highest student-share group-এ:

```text
Overall LL = 0.539
Negative LL = 1.154
FPR = 85.01%
```

অর্থাৎ student participation বেশি হলে overall score ভালো, কিন্তু incorrect objective rejection খারাপ।

এটি consistent with:

> Model student participation/engagement-এর general signal-কে positive mastery signal হিসেবে ব্যবহার করতে পারে, objective-specific mastery হিসেবে নয়।

এখানে বলা যাবে না tutor instruction harmful বা student বেশি কথা বললে performance খারাপ। এগুলো association, causal evidence নয়।

[Student–tutor summary](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/student_tutor_behavior/all_behavior_group_summary.csv)

---

# 8. Transcript-noise proxies মূল problem নয়

Noise variables manual annotation নয়; এগুলো proxy।

যা পাওয়া গেছে:

* Very high student-short-turn ratio stable high-risk;
* Very high turns-per-minute stable high-risk;
* Low speaker-switch rate কিছুটা high-risk;
* High tutor streak group-এ small risk।

কিন্তু continuous results:

| Variable              | Spearman rho |    Bootstrap CI |
| --------------------- | -----------: | --------------: |
| Background-turn ratio |      −0.0038 | [−0.018, 0.010] |
| Tutor-streak ratio    |       0.0104 | [−0.002, 0.023] |

CI zero cross করেছে। অর্থাৎ background turns বা tutor streak-এর clear monotonic effect নেই।

তাই broad transcript cleaning/noise removal এখন first priority হওয়া উচিত নয়।

সীমিতভাবে:

* very high turns-per-minute;
* very short student turns;
* fragmented student responses;

manual review করা যেতে পারে।

[Noise summary](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/transcript_noise/all_noise_proxy_summary.csv) · [Continuous trends](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/continuous_trends/continuous_spearman_summary.csv)

---

# 9. Intersection analysis থেকে কী পেলাম?

72টি possible intersection cell-এর মধ্যে 62টি support threshold pass করেছে।

সবচেয়ে বড় observed interaction:

```text
Long transcript × Very rare objective
Interaction excess = +0.068
```

কিন্তু bootstrap CI:

```text
[-0.003, 0.147]
```

Zero cross করেছে, তাই strong-looking হলেও statistically uncertain।

তুলনামূলকভাবে stronger supported interactions:

| Intersection                                    | Excess | 95% bootstrap CI |
| ----------------------------------------------- | -----: | ---------------: |
| Very rare objective × 2 objectives/session      | +0.060 |   [0.001, 0.121] |
| Very long transcript × medium-support objective | +0.020 |   [0.005, 0.035] |
| High background ratio × long transcript         | +0.015 |   [0.000, 0.030] |

Interpretation:

> কিছু combinations additive expectation-এর চেয়ে খারাপ, কিন্তু effects অধিকাংশ ক্ষেত্রে ছোট এবং exploratory।

এগুলো model redesign-এর primary basis না করে hard-case sampling ও targeted validation-এর basis করা ভালো।

[Intersection registry](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/intersections/intersection_cell_registry.csv)

---

# 10. Research-এর মূল সমস্যাগুলো priority অনুযায়ী

## Critical Problem 1 — False-positive dominance

Evidence:

```text
Overall FPR = 81.04%
Negative LL = 1.095
Balanced accuracy = 56.84%
```

### কী করতে হবে

* negative examples-এর training weight বাড়ানো;
* same-session hard negative oversampling;
* high-confidence false positives আলাদা করে retrain set-এ যোগ করা;
* validation fold-এ probability calibration;
* hard prediction প্রয়োজন হলে threshold tune করা।

তবে শুধু threshold change করলে Log Loss improve হবে না। Probability quality improve করতে training/calibration দরকার।

---

## Critical Problem 2 — Objective-specific discrimination failure

Evidence:

```text
Mixed-label FPR = 92.32%
Mixed-session collapse = 74.93%
5+ objective FPR = 98.33%
5+ mixed-session collapse = 88.71%
```

### সবচেয়ে গুরুত্বপূর্ণ model upgrade

**একই session-এর correct এবং incorrect objectives-কে hard positive–negative pairs হিসেবে train করা।**

Loss হতে পারে:

[
L
=

L_{\text{classification}}
+
\lambda L_{\text{pairwise ranking}}
]

যেখানে correct objective probability incorrect objective probability-এর চেয়ে margin সহ বেশি হতে হবে।

আরও দরকার:

* within-session contrastive loss;
* same-session hard-negative mining;
* objective-conditioned evidence retrieval;
* correct objective বনাম closest incorrect objective comparison।

---

## High Priority Problem 3 — Model general transcript positivity ধরছে

Model সম্ভবত tutor explanation, positive wording, দীর্ঘ participation বা general engagement-কে mastery evidence হিসেবে ব্যবহার করছে।

### সমাধান

* student utterance ও tutor utterance আলাদা representation;
* student-only evidence view;
* tutor text context হিসেবে রাখা, mastery evidence হিসেবে নয়;
* objective অনুযায়ী relevant student turns select করা;
* evidence attribution/checking যোগ করা।

---

## High Priority Problem 4 — Rare-objective generalization

### সমাধান

* response-weighted loss-এর পাশাপাশি objective-macro loss;
* rare objectives balanced sampling;
* objective text semantic embeddings;
* related objectives থেকে retrieval;
* leave-one-objective-out validation;
* rare/unseen objectives-এর জন্য uncertainty flag।

---

## High Priority Problem 5 — Long and complex sessions

Naive truncation করা ঠিক হবে না, কারণ long transcript overall positive examples-এ useful।

### সমাধান

* transcript chunking;
* hierarchical encoder;
* objective-conditioned relevant-chunk retrieval;
* student-turn filtering;
* top-k evidence selection;
* session-level objective ranking।

---

## Medium Priority — Behavioural structure

Low student evidence, short responses এবং fragmented turns কিছু risk দেখায়।

### সমাধান

* student evidence quantity/quality features;
* answer-after-question linkage;
* turn relevance score;
* tutor question-এর পর student response বেশি গুরুত্ব দেওয়া।

---

## Lower Priority / Inconclusive — General noise cleaning

Background-turn ratio এবং tutor streak-এর continuous evidence weak। তাই এখন full-scale noise-removal pipeline বানানোর আগে manual review দরকার।

---

# Research quality ও limitations

কিছু গুরুত্বপূর্ণ সীমাবদ্ধতা:

* Provider, domain, grade, curriculum এবং source metadata dataset-এ নেই; analysis সঠিকভাবে skipped হয়েছে।
  [Provider/domain status](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/provider_domain/provider_domain_status.json)

* Unseen objective group-এ মাত্র 83 responses; definitive conclusion দেওয়া যাবে না।

* Noise variables confirmed noise labels নয়।

* Intersection excess exploratory; causal interaction নয়।

* Continuous trend atlas-এ Spearman bootstrap CI আছে, কিন্তু individual trend bins-এর uncertainty interval save করা হয়নি। তাই bin-level lines descriptive।

* 92 registered group-এর মধ্যে 89টিতে raw accuracy বনাম balanced accuracy materially different flag হয়েছে। তাই future reporting-এ raw accuracy primary metric হওয়া উচিত নয়।
  [Imbalance flags](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/class_conditional_prevalence/imbalance_flags.csv)

---

# সবাইকে দেখানোর জন্য সবচেয়ে গুরুত্বপূর্ণ ৩টি chart

## 1. Error Direction Butterfly — সবচেয়ে গুরুত্বপূর্ণ

[দেখুন: Error Direction Butterfly](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/class_conditional_prevalence/error_direction_butterfly.png)

### এই chart-এর message

> প্রায় প্রতিটি supported group-এই false-positive rate অনেক বড় এবং false-negative rate ছোট।

বিশেষ করে:

* 5+ objectives;
* 3–4 objectives;
* mixed-label;
* very rare objective;

সব জায়গাতেই right-side false-positive bars dominant।

Presentation-এ প্রথমে এই chart দেখানো উচিত। এটি পুরো research-এর primary problem এক নজরে বোঝায়।

---

## 2. Class-Specific Loss Dumbbell Forest

[দেখুন: Class-Specific Loss Dumbbell](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/class_conditional_prevalence/class_loss_dumbbell_forest.png)

### এই chart-এর message

> Overall score একই হলেও positive-class এবং negative-class behaviour এক নয়।

সবচেয়ে striking:

```text
5+ objectives:
Positive-class loss overall-এর চেয়ে অনেক ভালো
Negative-class loss overall-এর চেয়ে প্রায় +0.61 বেশি
```

Mixed-label এবং very rare objectives-এর negative-class deterioration-ও পরিষ্কার।

এই chart বুঝিয়ে দেয় কেন overall Log Loss বা accuracy একা দেখানো dangerous।

---

## 3. Step 5 Mechanism Linkage

[দেখুন: Step 5 Mechanism Linkage](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/step5_linkage/step5_mechanism_linkage.png)

### এই chart-এর message

> High-risk groups শুধু high-loss নয়; এগুলোতে session margin কম, collapse বেশি এবং incorrect objective probability বেশি।

এটি technical audience, supervisor বা team discussion-এর জন্য সবচেয়ে useful। কারণ এটি problem-এর **mechanism** দেখায়।

General/nontechnical audience-এর জন্য এর পরিবর্তে এই সহজ chart ব্যবহার করা যেতে পারে:

[Alternative: Log Loss by Session Label Structure](sandbox:/mnt/data/06_group_analysis_extracted/06_group_analysis/session_complexity/figures/label_structure_log_loss.png)

---

# এক বাক্যে final research conclusion

> **Baseline model positive responses ভালোভাবে শনাক্ত করলেও negative objectives reject করতে ব্যর্থ হচ্ছে; এই failure mixed-label ও multi-objective sessions-এ objective collapse হিসেবে সবচেয়ে বেশি প্রকাশ পাচ্ছে, এবং rare-objective ও limited student-evidence groups-এ risk আরও বাড়ছে। তাই V2 model-এর প্রথম priority হওয়া উচিত same-session hard negatives, objective-conditioned evidence selection, pairwise/contrastive ranking loss এবং negative-class calibration।**

# Trace the Ace — Scratch Mastery Phase
## গভীর গবেষণা ও Master Model তৈরির পূর্ণাঙ্গ রোডম্যাপ

> **নথির উদ্দেশ্য:** Baseline phase-এ পাওয়া ফলাফল, সমস্যা ও সীমাবদ্ধতাকে ভিত্তি করে একটি নতুন, evidence-driven, leakage-safe এবং objective-conditioned master modelling workflow তৈরি করা।

---

## ১. Baseline Diagnosis এবং Non-negotiable Constraints

Baseline phase-এর সবচেয়ে বড় অর্জন শুধু এই নয় যে বর্তমান model অসম্পূর্ণ—বরং আমরা পরিষ্কারভাবে বুঝতে পেরেছি **model কোথায় এবং কীভাবে ব্যর্থ হচ্ছে**। Official taskটি response-level prediction: প্রতিটি sample একটি নির্দিষ্ট `session × learning objective` combination, কিন্তু একই tutoring session থেকে একাধিক labelled response তৈরি হতে পারে। Transcript-এ ordered utterance, speaker role এবং timestamp দেওয়া থাকে। Competition-এর লক্ষ্য হলো objective description-এর সাধারণ prior ব্যবহার না করে transcript-এর ভেতর থেকে objective-specific evidence শনাক্ত করা। Official ranking metric হলো **Log Loss**, তাই ভুল prediction-এর সঙ্গে অতিরিক্ত confidence থাকলে penalty অনেক বেশি হয়।[^competition-task]

এই audit-এ বিশেষভাবে নিচের notebooks, reports এবং diagnostic outputs review করা হয়েছে:

- `Data_integration(1).ipynb`
- `1_model_training(5).ipynb`
- `1_hyperparameter_tuning(7).ipynb`
- `baseline_model_analysis(2).ipynb`
- `baseline_analysis_2(3).ipynb`
- `Step_7_Integrated_Diagnostic_8_Cells (1)(1).ipynb`
- `trace_the_ace_complete_steps_0_7_analysis(1).md`
- `step5 research(2).md`
- Final baseline report এবং baseline failure analysis PDF

### বর্তমান dataset ও performance অবস্থান

| বিষয় | Audited result |
|---|---:|
| Response-level sample | 35,072 |
| Session | 22,821 |
| Positive-label rate | 70.25% |
| Initial train/validation split | 28,125 / 6,947 |
| Constant-prior Log Loss | 0.5986 |
| Structured model Log Loss | প্রায় 0.5924 |
| Word TF–IDF logistic Log Loss | 0.5455 |
| Character TF–IDF logistic Log Loss | 0.5557 |
| Tuned word + character Log Loss | 0.5482 |
| Five-fold grouped OOF Log Loss | 0.55546 |
| Project report-এ recorded public leaderboard Log Loss | 0.6163 |

Official reference analysis আমাদের project-এর দুটি গুরুত্বপূর্ণ methodological finding-কে সমর্থন করে। প্রথমত, response row ধরে random split করলে একই session-এর তথ্য train ও validation-এ চলে যেতে পারে; তাই session-level grouping জরুরি। দ্বিতীয়ত, student-talk সম্পর্কিত কিছু simple feature signal দেয়, কিন্তু এগুলো একা individual outcome explain করতে পারে না। উদাহরণস্বরূপ, দীর্ঘ explanation এবং reasoning-এর মধ্যে ব্যবহৃত number, শুধু ছোট ছোট numerical answer-এর pattern থেকে আলাদা signal দেয়; তবে এগুলো association, causal tutoring effect নয়।[^reference-analysis]

### Baseline-এর central failure: Objective-conditioning failure

বর্তমান model input হিসেবে নেয়:

```text
[OBJECTIVE] learning objective
[TRANSCRIPT] complete flattened conversation
```

কিন্তু বাস্তবে model-এর behaviour অনেকটা এমন:

```text
general session impression
        +
objective difficulty / topic prior
        =
prediction
```

যেখানে আমাদের প্রয়োজন ছিল:

```text
evidence in this conversation
        ×
this particular objective
        =
objective-specific mastery probability
```

এই conclusion project diagnostics-এর কয়েকটি শক্তিশালী result দ্বারা সমর্থিত:

| Diagnostic | Audited result | Interpretation |
|---|---:|---|
| Between-session share of prediction variation | 99.67% | Session বদলালে prediction বেশি বদলায় |
| Within-session variation | প্রায় 0.33% | একই session-এ objective বদলালেও prediction খুব কম বদলায় |
| Transcript-dominance score | প্রায় 94.5% | General session language prediction-কে dominate করে |
| Mixed-label session | 3,207 | Objective discrimination test করার সবচেয়ে গুরুত্বপূর্ণ group |
| Same-session positive–negative pair | 5,323 | Natural hard-negative pair ইতোমধ্যে dataset-এ আছে |
| Median same-session probability margin | 0.0051 | Correct ও incorrect objective প্রায় একই score পায় |
| Session-collapse rate | 74.93% | অধিকাংশ mixed session-এ meaningful separation নেই |
| Pairwise reversal rate | 32.07% | Incorrect objective প্রায় এক-তৃতীয়াংশ pair-এ correct objective-কে outrank করে |

### Positive bias শুধু class imbalance-এর ফল নয়

Dataset-এ positive label প্রায় 70%, কিন্তু model প্রায় **90.65% response-কে positive predict করে**। False-positive rate **81.04%**; positive-class Log Loss প্রায় **0.327**, negative-class Log Loss প্রায় **1.095**, এবং false positives মোট OOF loss-এর প্রায় **53.05%** তৈরি করে। Lexical evidence apply হওয়ার আগেই model-এর base probability প্রায় **0.676**। এরপর positive-looking language, objective prevalence এবং general session quality এই positive starting point-কে আরও শক্তিশালী করে। অন্যদিকে uncertainty, contradiction, guessing, unresolved error এবং tutor-led correction-এর মতো negative meaning probability যথেষ্ট কমাতে পারে না।

Positive bias-এর সম্ভাব্য চারটি connected source:

| Source | Mechanism |
|---|---|
| Label prevalence | Population-level positive intercept statistically reasonable |
| Objective prior | Frequently successful বা সহজ objective evidence দেখার আগেই high probability পায় |
| Transcript-wide positivity | Engagement, tutor explanation ও relevant vocabulary-কে learning success মনে করা হয় |
| Weak negative semantics | Confusion, correction, hesitation ও contradiction probability যথেষ্ট কমাতে পারে না |

SHAP এবং loss-budget analysis দেখায়, objective-linked contribution তুলনামূলক কম; tutor/shared lexical language contribution-এর বড় অংশ dominate করে। Lexical-amplified false positives false-positive loss-এর প্রায় **48.05%** এবং মোট OOF loss-এর **25.49%** তৈরি করে। তবে এটি **tutor speech ক্ষতিকর**—এমন causal proof নয়। সঠিক conclusion হলো: বর্তমান representation tutor support এবং student mastery-কে নির্ভরযোগ্যভাবে আলাদা করতে পারে না।

### Leakage ও validation audit

Implemented grouped evaluation-এ direct session leakage-এর evidence পাওয়া যায়নি। Initial split-এ train ও validation session overlap ছিল শূন্য; পরে five-fold grouped evaluation করা হয়েছে। Preprocessor এবং vectorizer training partition-এর উপর fit করা হয়েছে। তবে subtle validation risk এখনো আছে:

| Validation risk | Assessment |
|---|---|
| একই session train ও validation-এ | Audited split-এ সঠিকভাবে prevent করা হয়েছে |
| Single-holdout optimism | Confirmed; grouped OOF initial holdout-এর চেয়ে খারাপ |
| Objective statistics globally fit করা | নতুন pipeline-এ নিষিদ্ধ; সব prior fold-specific হতে হবে |
| আলাদা session ID-তে near-duplicate transcript | এখনো পূর্ণ audit হয়নি |
| Near-identical objective description fold পার হওয়া | Expected; seen/rare/unseen-objective analysis প্রয়োজন |
| এক split-এর উপর hyperparameter search | Master phase-এর জন্য খুব fragile |
| Model-selection data-তেই calibration | Nested বা OOF-only হতে হবে |
| Test-set adaptation | Competition rule অনুযায়ী নিষিদ্ধ |
| Environment mismatch | Current notebook Python 3.10 / scikit-learn 1.7.2; submission runtime Python 3.12 |

Competition submission-এ প্রতিটি test sample স্বাধীনভাবে process করতে হবে। Test pseudo-labelling, test examples-এর মধ্যে unsupervised adaptation এবং test-derived aggregate feature নিষিদ্ধ। Inference automatic হতে হবে; test-time retraining করা যাবে না।[^competition-rules]

### Baseline থেকে যা রাখা হবে

- Word TF–IDF logistic model: ensemble component ও diagnostic control হিসেবে
- Session-grouped validation
- Learning objective text
- Ordered raw utterances
- Speaker roles
- Timestamps
- OOF prediction storage
- Class-specific error analysis
- Student word volume, explanation-vs-answer-only numerical behaviour এবং dialogue structure-এর মতো stable features—তবে controlled validation সহ[^reference-analysis]

### যা সম্পূর্ণ পরিবর্তন করতে হবে

- পুরো transcript একটিমাত্র undifferentiated text field হিসেবে flatten করা যাবে না
- Student ও tutor speech একটি aggregated block-এ merge করা যাবে না
- Retrieval actual ordered utterance থেকে পুনর্গঠন করতে হবে
- Names, IDs এবং template artefact unrestricted lexical shortcut হিসেবে রাখা যাবে না
- Calibration-কে primary repair হিসেবে ধরা যাবে না
- Representation বদলানোর আগে broad hyperparameter tuning করা যাবে না

> **Scratch Mastery Phase আরেকটি classifier tune করে শুরু করা যাবে না। প্রথম কাজ হবে evidence unit-কে সঠিকভাবে পুনর্গঠন করা।**

---

## ২. Advanced EDA এবং Data-repair Programme

Official files-এ utterance order, role, content এবং timestamp সংরক্ষিত আছে। কিন্তু আগের retrieval diagnostic প্রায় প্রতিটি session-কে একটি aggregated student block এবং একটি aggregated tutor block-এ পরিণত করেছিল। ফলে retrieval overlap, temporal evidence এবং pre/post-feedback analysis বৈধ turn-level experiment ছিল না। তাই Scratch Mastery Phase-এর প্রথম artefact model নয়—একটি canonical **turn table**।[^competition-task]

### Canonical analytical tables

| Table | Analysis unit | Essential fields |
|---|---|---|
| `responses` | Session–objective response | response ID, session ID, objective, label |
| `turns` | Individual utterance | session ID, utterance ID, role, text, timestamp, sequential index |
| `sessions` | Tutoring session | length, duration, role counts, dialogue structure |
| `objective_turn_pairs` | Objective × turn | lexical similarity, semantic similarity, role, relative position |
| `session_objective_pairs` | একই session-এর objective pair | labels, probability margin, evidence overlap |
| `objective_catalogue` | Canonical objective | frequency, label rate, semantic cluster, neighbouring objectives |
| `oof_errors` | Response | OOF probability, loss, FP/FN type, subgroup membership |

সব derived table deterministic code দিয়ে তৈরি হবে। প্রতিটি join-এর cardinality, row count এবং key uniqueness assert করতে হবে। প্রতিটি transformation একটি compact audit manifest তৈরি করবে, যেখানে থাকবে:

- Input file hash
- Pipeline version
- Row count
- Null count
- Duplicate count
- Split ID
- Timestamp / run ID

### Turn reconstruction এবং text-quality audit

Turn parser-এর নিয়ম:

1. প্রথমে timestamp অনুযায়ী sort
2. একই timestamp হলে utterance ID tie-breaker
3. Sequential turn index তৈরি
4. Speaker role preserve
5. Original text অপরিবর্তিত রাখা; cleaned text আলাদা column-এ

Quality checks:

- Timestamp monotonicity
- Duplicate utterance ID
- Missing role
- Empty content
- `[UNCLEAR]` frequency
- Repeated ASR fragment
- অস্বাভাবিক দীর্ঘ utterance
- Abrupt speaker switch
- Consecutive duplicated turn
- Impossible or zero session duration

Lexical heuristic দিয়ে speaker-role mismatch diagnostic করা যেতে পারে; strong evidence ছাড়া original role automaticভাবে বদলানো যাবে না।

Analysis-এ অন্তত নিচের sequence আলাদা করতে হবে:

```text
student evidence before tutor feedback
        ↓
tutor question / prompt
        ↓
student attempt
        ↓
tutor correction / confirmation / scaffold
        ↓
student response after feedback
        ↓
final student evidence
```

এই sequence total word count-এর তুলনায় বেশি informative। Official reference analysis-ও timing, final reasoning এবং correction-এর পরে student evidence-কে future analysis-এর গুরুত্বপূর্ণ direction হিসেবে উল্লেখ করেছে।[^reference-analysis]

### Multi-level EDA

| Level | প্রধান প্রশ্ন | গুরুত্বপূর্ণ output |
|---|---|---|
| Response level | Positive ও negative session–objective pair-এর বাস্তব পার্থক্য কী? | OOF loss, evidence coverage, contradiction, final-answer evidence |
| Session level | কোন session uniformly high, mixed outcome বা collapse তৈরি করে? | Session type, objective count, within-session margin |
| Objective level | কোন objective common, rare, difficult, ambiguous বা unseen? | Fold-safe prior, macro Log Loss, semantic cluster |
| Turn level | কোন student/tutor turn objective-এর সঙ্গে aligned? | Relevance, role, temporal position, dialogue function |
| Pair level | একই session-এ একটি objective correct এবং অন্যটি incorrect কেন? | Differential evidence, retrieval overlap, contradiction difference |

Advanced EDA-এর central question হবে না:

> Positive transcript কি negative transcript-এর চেয়ে বড়?

বরং হবে:

> **একই session-এর মধ্যে positive objective-কে support করে—কিন্তু negative objective-কে support করে না—এমন evidence কোনটি?**

এই controlled comparison tutor identity, general engagement, transcript length এবং session quality-এর অনেক confounding কমায়।

### Hard-example taxonomy

প্রতিটি OOF response-কে এক বা একাধিক deterministic diagnostic label দিতে হবে:

| Case type | Definition | ব্যবহার |
|---|---|---|
| Confident false positive | `y=0`, কিন্তু high OOF probability | Primary Log Loss target |
| Confident false negative | `y=1`, কিন্তু low OOF probability | Overcorrection প্রতিরোধ |
| Collapsed positive | Correct objective একই session-এর incorrect objective-এর খুব কাছে | Objective discrimination |
| Reversed pair | Incorrect objective correct objective-এর উপরে ranked | Hard-negative training |
| Prior-dominant error | Contradictory evidence থাকা সত্ত্বেও prediction prior-এর কাছাকাছি | Prior gating |
| Lexical-amplified error | Positive lexical cue positive prior আরও বাড়ায় | Shortcut detection |
| Evidence-sparse response | Objective-matching student evidence নেই বা খুব দুর্বল | Missing-evidence handling |
| Tutor-only support | Objective প্রধানত tutor turn-এ উপস্থিত | Instruction বনাম mastery separation |
| Post-correction-only evidence | Student evidence শুধু heavy tutor support-এর পরে আসে | Assistance sensitivity |
| Label-suspicious case | Near-identical evidence কিন্তু conflicting label | Noise review |

Overall Log Loss improve হলেও যদি confident negative error, mixed-session collapse বা same-session reversal খারাপ হয়, model promote করা যাবে না।

### Duplicate, contradiction এবং label-noise analysis

চার ধরনের duplicate audit করতে হবে:

| Audit | পদ্ধতি |
|---|---|
| Exact session duplicate | Normalised transcript hash |
| Near-duplicate session | MinHash / character n-gram similarity, পরে embedding confirmation |
| Exact objective duplicate | Lowercase + punctuation/whitespace canonicalisation |
| Semantic objective duplicate | Sentence embedding + high-similarity cluster manual review |

Near-duplicate session যদি ভিন্ন fold-এ থাকে, তাহলে objective set এবং label consistency measure করতে হবে। Duplicate automatically remove করা যাবে না—কারণ repeated instructional template legitimate হতে পারে। তবে duplicate-cluster grouped stress split দিয়ে দেখতে হবে model repeated text memorise করছে কি না।

Label inconsistency flag করতে হবে যখন:

- Near-identical session–objective evidence conflicting label পায়
- একাধিক independent model একই row-এর label-এর বিপরীতে খুব confident prediction দেয়
- Same-session semantically duplicate objective conflicting label পায়

এগুলো **automatic relabelling candidate নয়**; manual review candidate। কারণ target future quiz outcome, তাই in-session correct response থাকা সত্ত্বেও final label negative হওয়া বৈধ হতে পারে।

### Shortcut এবং hidden-pattern audit

SHAP alone যথেষ্ট নয়। প্রতিটি shortcut controlled experiment দিয়ে test করতে হবে:

| Suspected shortcut | Proper test |
|---|---|
| Objective historical difficulty | Fold-safe objective-prior-only model |
| Tutor/student names | Name placeholder করে retrain |
| Speaker markers | Marker format standardise করে retrain |
| Repeated lesson template | Duplicate-cluster holdout |
| Session length | Length-matched positive/negative comparison |
| Objective keywords | Objective paraphrase / canonical-concept experiment |
| Tutor verbosity | Objective ও length controlled comparison |
| Student numerical answers | Answer-only number বনাম reasoning-embedded number |
| Generic positive words | Negation-aware, role-aware ablation |
| Transcript-only judgement | Same session-এর মধ্যে objective swap test |

Objective-swap test বিশেষভাবে গুরুত্বপূর্ণ। একটি mixed-label session-এর একই evidence-এর সঙ্গে session-এর প্রতিটি objective বসিয়ে score পরিবর্তন দেখা হবে। Objective-conditioned model হলে objective বদলালে meaningful ও সঠিক direction-এ score separation তৈরি হওয়া উচিত।

### Test data নিয়ে নিষিদ্ধ analysis

Train-vs-test adversarial validation-এ aggregate test information ব্যবহার করা যাবে না। Competition rule অনুযায়ী test sample independentভাবে process করতে হবে এবং aggregate test-derived learning নিষিদ্ধ। তাই distribution-shift analysis training-only stress fold দিয়ে করতে হবে:

- Rare-objective fold
- Semantic objective-cluster fold
- Duplicate-cluster fold
- Extreme transcript-length fold
- High-objective-count session fold

[^competition-rules]

### Manual review protocol

আগের blank templates-এর পরিবর্তে stratified double-review প্রয়োজন। মোট প্রায় **150–250টি carefully selected case** একটি high-value diagnostic sample তৈরি করতে পারে:

| Stratum | Suggested share |
|---|---:|
| Confident false positive | 30% |
| Same-session collapsed/reversed pair | 25% |
| Confident false negative | 15% |
| Rare objective | 10% |
| Very long বা evidence-sparse session | 10% |
| Correct high-confidence control | 10% |

Review labels:

- Objective coverage
- Student evidence strength
- Tutor assistance level
- Contradiction
- Guessing
- Correction
- Independent recovery
- Possible label ambiguity
- Parser issue
- Other

কমপক্ষে একটি subset দুইজন reviewer independently annotate করবে। Agreement measure ছাড়া manual labels-কে training target বা confirmed ground truth হিসেবে ব্যবহার করা যাবে না।

---

## ৩. Advanced Feature System এবং Auxiliary Dataset Strategy

Master feature system-এ তিনটি layer থাকবে:

1. **Evidence retrieval** — objective-এর সঙ্গে কোন turn relevant তা খুঁজে বের করা
2. **Semantic interpretation** — evidence support, contradiction, uncertainty বা assistance বোঝা
3. **Calibrated prior/context features** — objective difficulty ও session context নিরাপদভাবে ব্যবহার করা

বর্তমান TF–IDF representation মূলত জিজ্ঞাসা করে: “এই শব্দগুলো আছে কি?” নতুন system-কে জিজ্ঞাসা করতে হবে:

- Student objective-টি demonstrate করেছে কি?
- Evidence objective-কে support করে, contradict করে, নাকি irrelevant?
- Tutor কতটা help করেছে?
- Student independently reasoning করেছে, নাকি answer repeat করেছে?
- একই session-এর অন্য objective-এর তুলনায় এই objective-এর evidence কতটা specific?

### ৩.১ Objective-conditioned evidence retrieval

প্রতিটি objective-এর জন্য প্রতিটি turn score করতে হবে নিচের signal দিয়ে:

- Sparse word overlap
- Character overlap
- Mathematical token overlap
- Semantic cosine similarity
- Objective concept coverage
- Speaker role
- Relative temporal position
- Adjacent question–answer relationship
- Turn-এর আগে/পরে tutor feedback
- Final-segment proximity
- Student vs tutor evidence source

First-stage retrieval-এর জন্য sentence-transformer bi-encoder উপযুক্ত, কারণ turn embeddings আগে থেকেই precompute করা যায় এবং objective embedding-এর সঙ্গে দ্রুত similarity calculate করা যায়। Sentence-BERT semantic search ও sentence similarity scalable করার জন্যই তৈরি হয়েছিল।[^sbert]

প্রাথমিক design:

- Top 8 student turns
- Top 4 tutor turns
- প্রতিটি selected turn-এর একটি previous এবং একটি next neighbour
- Overall token budget-এর মধ্যে final student segment বাধ্যতামূলকভাবে অন্তর্ভুক্ত

তারপর cross-encoder shortlist rerank করবে। Cross-encoder objective এবং candidate evidence একসঙ্গে পড়তে পারে, তাই pairwise relevance বেশি accurately score করে; তবে এটি bi-encoder-এর চেয়ে ধীর। তাই standard workflow হবে:

```text
Bi-encoder retrieval
        ↓
Short candidate list
        ↓
Cross-encoder reranking
```

[^cross-encoder]

### ৩.২ Lexical ও mathematical features

Baseline-এর useful lexical signal রাখা হবে, কিন্তু role-, time- এবং objective-aware করে:

| Feature family | উদাহরণ |
|---|---|
| Objective overlap | Student/objective TF–IDF cosine, tutor/objective cosine, matched concept count |
| Mathematical content | Symbol, fraction, equation, unit, number word, operation term |
| Explanation depth | Causal connective, multi-clause answer, reasoning verb, “because/so/therefore” |
| Answer-only behaviour | Single-token answer, isolated number, repeated guess |
| Uncertainty | “maybe”, “I think”, hedge, student question |
| Negation ও failure | “not”, “don’t know”, “wrong”, “confused”, correction request |
| Self-correction | Tutor answer প্রকাশের আগে student নিজে answer পরিবর্তন করেছে কি না |
| Tutor dependence | Objective-relevant window-এ tutor-to-student word ratio |
| Feedback response | Correction/scaffold-এর পরে student response |
| Completion | Final student evidence-এ objective concept উপস্থিত কি না |
| Contradiction | Incompatible calculation, negated objective claim, tutor rejection |
| Coherence | Relevant student turns পরস্পরের সঙ্গে consistent কি না |
| Evidence concentration | একটি strong turn-এ concentrated, নাকি transcript জুড়ে diffuse |

Official reference analysis substantive reasoning এবং short answer-only numerical response-এর মধ্যে distinction useful হতে পারে বলে দেখিয়েছে। তবে simple count causal explanation নয়; controlled experiment দরকার।[^reference-analysis]

### ৩.৩ Semantic এবং interaction features

সবচেয়ে গুরুত্বপূর্ণ feature standalone count নয়—**comparison feature**:

$$
\text{student-objective alignment}
-
\text{tutor-objective alignment}
$$

$$
\text{entailment / support}
-
\text{contradiction / uncertainty}
$$

$$
\text{student evidence after feedback}
-
\text{student evidence before feedback}
$$

$$
\text{correct-objective evidence}
-
\text{same-session hard-negative evidence}
$$

Recommended interaction features:

| Feature | Intended meaning |
|---|---|
| `student_support_max` | Objective-এর জন্য strongest student evidence |
| `student_support_topk_mean` | একাধিক turn-এ support consistent কি না |
| `student_contradiction_max` | Strongest negative semantic cue |
| `tutor_support_minus_student_support` | Tutor objective cover করেছে, কিন্তু student mastery নেই |
| `post_feedback_gain` | Assistance-এর পরে student evidence improve করেছে কি না |
| `final_segment_support` | Session-এর শেষের দিকে objective evidence |
| `evidence_role_entropy` | Relevant language student-led নাকি tutor-led |
| `objective_retrieval_margin` | এই objective বনাম same-session alternatives-এর evidence difference |
| `within_session_prior_adjusted_score` | Session-wide positivity বাদ দিয়ে semantic evidence |
| `hard_negative_similarity` | অন্য objective একই evidence দিয়ে কত সহজে explain করা যায় |

Natural Language Inference (NLI)-style training relevant, কারণ আমাদের distinction অনেকটা support/entailment, contradiction এবং neutral-এর মতো। Contrastive sentence-learning research দেখিয়েছে entailment pair positive এবং contradiction hard negative হিসেবে ব্যবহার করা যায়। এটি objective–evidence representation-এর জন্য সরাসরি useful।[^simcse]

### ৩.৪ Fold-safe objective prior

Objective-only model-এর ভালো performance উপেক্ষা করা যাবে না। এটি দেখায় objective difficulty বা historical success rate-এর বাস্তব predictive value আছে। সমস্যা হলো prior যেন semantic evidence-কে dominate না করে।

প্রতিটি training fold-এ smoothed objective prior শুধু সেই fold-এর training sessions থেকে calculate করতে হবে:

$$
p_o = \frac{n_o^+ + \alpha p_{\mathrm{global}}}{n_o + \alpha}
$$

এখানে:

- $n_o^+$ = objective $o$-এর positive count
- $n_o$ = objective $o$-এর মোট training count
- $p_{\mathrm{global}}$ = training fold-এর global positive rate
- $\alpha$ = shrinkage strength

Rare objective-এর prior global rate-এর দিকে shrink করবে। Test inference-এর সময় prior সব training data থেকে fit হবে। Unseen objective global prior ব্যবহার করবে; semantic-neighbour prior শুধু কঠোর OOF validation-এ লাভ প্রমাণ হলে ব্যবহার করা যাবে।

Prior-কে text-এর মধ্যে embed না করে separate numeric feature হিসেবে রাখতে হবে। Model head শিখবে কখন evidence prior override করবে। Strong contradiction বা support থাকা সত্ত্বেও prediction যদি prior-এর কাছাকাছি আটকে থাকে, তাহলে regularisation penalty দেওয়া যেতে পারে।

### ৩.৫ কোন feature বাদ বা সীমিত করতে হবে

| Feature | Decision |
|---|---|
| `response_id`, raw `session_id` | Exclude |
| Personal name | Role-preserving placeholder-এ normalise |
| Raw objective identifier | Exclude; objective text ও fold-safe prior ব্যবহার |
| Global objective label mean | সম্পূর্ণ নিষিদ্ধ |
| Test-set objective frequency | নিষিদ্ধ |
| Full flattened transcript | Sole transformer input হিসেবে ব্যবহার করা যাবে না |
| Tutor praise count | Role/context-aware controlled validation ছাড়া নয় |
| Raw transcript length | Low-capacity context feature হিসেবে সীমিত |
| LLM-generated binary prediction | Unverified direct feature হিসেবে নয় |
| Previous OOF prediction | Proper cross-fitted stacking ছাড়া নয় |

### ৩.৬ LLM-assisted features

LLM-এর সবচেয়ে practical ব্যবহার final predictor হিসেবে নয়; বরং **training-data annotator বা teacher** হিসেবে। Official reference analysis-ও turn-level explanation quality annotate করে ছোট interpretable model train করার সম্ভাবনা উল্লেখ করেছে।[^reference-analysis]

একটি fixed, openly licensed local model training turns-এ নিচের weak labels তৈরি করতে পারে:

- Objective relevance
- Student understanding / support
- Contradiction / uncertainty
- Tutor answer reveal করেছে কি না
- Explanation completeness
- Student independently recover করেছে কি না
- Likely tutoring move

Safety rules:

1. Versioned prompt
2. Deterministic decoding
3. Response label prompt-এ দেওয়া যাবে না
4. OOF বা future outcome information দেওয়া যাবে না
5. Repeated-run consistency audit
6. Human-reviewed sample
7. Final inference-এ direct expensive LLM prompting এড়িয়ে ছোট student classifier/distillation

LLM-derived feature-এর risk:

- Prompt instability
- Mathematical hallucination
- Licence incompatibility
- High inference cost
- Hidden label leakage
- Training/test inconsistency
- API dependency

Competition runtime offline এবং internet access নেই; তাই proprietary API-based feature final submission-এর জন্য practical নয়। Model ও dependency local/preloaded হতে হবে।[^competition-runtime]

---

## ৪. Competition Ecosystem-এর অন্য ৯টি Dataset ব্যবহারের Strategy

Competition external data এবং pretrained model ব্যবহার অনুমতি দেয়, কিন্তু final/prize-eligible solution-এর resource licence broad use—বিশেষ করে commercial use—সমর্থন করতে হবে। Finalist-দের external resource declare করতে হবে।[^competition-rules]

### Dataset-by-dataset সিদ্ধান্ত

| Dataset | প্রাসঙ্গিকতা ও প্রস্তাবিত ব্যবহার | Main model-এর সঙ্গে connection | Expected benefit | Risk ও final decision |
|---|---|---|---|---|
| **Bridge** | Math tutoring conversation; mistake type ও correction strategy taxonomy | Manual annotation rubric ও error taxonomy design | Mistake, correction ও recovery বোঝার জন্য খুব relevant | CC BY-NC 4.0; final weight/feature নয়, research reference only[^bridge] |
| **DrawEduMath** | Hand-drawn math work ও QA annotation | Text-only dialogue task-এর সঙ্গে limited connection | Visual/error taxonomy idea | Non-commercial/share-alike + modality mismatch; final model থেকে exclude[^drawedumath] |
| **EssayJudge** | Math/science short essay ও lexical-quality annotation | Explanation richness/cohesion auxiliary head | Explanation-quality representation improve করতে পারে | Apache-2.0; domain shift বড়, low-weight auxiliary experiment only[^essayjudge] |
| **FairytaleQA** | Explicit ও implicit narrative question answering | Evidence retrieval pretraining | Direct vs implied evidence distinguish করতে সহায়তা | Apache-2.0; narrative shift বড়, low-priority retrieval experiment[^fairytaleqa] |
| **GSM8K** | Grade-school multi-step math solution | Math-step, operation, reasoning-chain intermediate training | Numerical reasoning ও answer-vs-explanation representation | MIT; tutoring speech থেকে style shift, direct label mapping নয়[^gsm8k] |
| **MRBench** | Math tutoring dialogue, ৮টি pedagogical dimension | Mistake, guidance, answer reveal, actionability, coherence auxiliary heads | Tutor support বনাম student mastery আলাদা করার জন্য সবচেয়ে relevant | CC BY-SA 4.0; derivative/share-alike implication organiser-এর কাছে লিখিতভাবে confirm করা প্রয়োজন[^mrbench] |
| **SciQ** | Science support text + correct/distractor answers | Support-vs-distractor / NLI pretraining | Negative-answer structure | CC BY-NC 3.0; prize model-এর জন্য unsafe, research-only[^sciq] |
| **SemEval short answers** | Correct, partial, contradictory, irrelevant, non-domain student answers | NLI/short-answer grading intermediate task | Mastery বনাম contradiction-এর সঙ্গে সরাসরি relevant | CC BY-SA 3.0; downstream weight licence confirmation ছাড়া final use নয়[^semeval] |
| **TalkMoves** | Classroom discourse move annotation | Question, revoicing, reasoning invitation, uptake detector | Tutor/student interaction structure | CC BY-NC-SA; taxonomy/rule design only, final training নয়[^talkmoves] |

### Safe first-wave external experiments

Published licence অনুযায়ী প্রথম wave-এ তুলনামূলক নিরাপদ:

1. **GSM8K**
2. **EssayJudge**
3. **FairytaleQA**

MRBench এবং SemEval technically খুব useful হতে পারে, কিন্তু final competition model-এ ব্যবহার করার আগে organiser-এর written licence clarification প্রয়োজন। Bridge, DrawEduMath, SciQ এবং TalkMoves non-commercial restriction-এর কারণে final trained weights বা learned features-এ ব্যবহার করা উচিত নয়।[^external-data-rules]

### External data কীভাবে connect হবে

অন্য dataset-এর label সরাসরি main 0/1 label-এর সঙ্গে concatenate করা যাবে না। Target definitions ভিন্ন। সঠিক strategy:

```text
External auxiliary task
        ↓
Shared language / evidence encoder
        ↓
Auxiliary head বাদ বা কম weight
        ↓
Trace the Ace training data-তে fine-tune
        ↓
Grouped OOF Log Loss ও mechanism metrics দিয়ে evaluation
```

প্রতিটি external-data experiment-এর paired control থাকতে হবে:

```text
Same architecture + same seed + no external pretraining
vs
Same architecture + same seed + external pretraining
```

External dataset শুধু তখনই retain হবে যখন:

- Overall OOF Log Loss improve করে
- অন্তত একটি mechanism metric improve করে
- Fold stability খারাপ না করে
- Negative-class loss worsen না করে
- Licence clear থাকে

---

## ৫. Model Shortlist এবং Recommended Master Architecture

Final system একটি monolithic large LLM হওয়া উচিত নয়। Dataset-এ 35,072 response row, long transcript, repeated session এবং strict offline inference constraint আছে। সবচেয়ে উপযুক্ত design হলো:

> **Hierarchical objective-conditioned encoder + retrieval + explicit prior + sparse ensemble component**

### ৫.১ Ranked model shortlist

| Rank | Candidate | Best role | Strength | Limitation | Recommendation |
|---:|---|---|---|---|---|
| 1 | **ModernBERT-base objective-conditioned encoder** | Main mastery classifier | Long context, encoder efficiency, classification/retrieval-friendly | Exact Python 3.12 runtime benchmark প্রয়োজন; long sequence এখনো expensive | Primary master model |
| 2 | **DeBERTa-v3-base cross-encoder** | Evidence reranker / compact classifier | Strong sentence-pair modelling, permissive licence, manageable size | Good retrieval/chunking ছাড়া compact context limit | Primary fallback ও ensemble member |
| 3 | **Sentence-transformer bi-encoder + cross-encoder** | Turn retrieval ও reranking | Fast semantic search + accurate pair scoring | Retrieval miss করলে evidence হারাতে পারে | Required subsystem |
| 4 | **Longformer-style hierarchical encoder** | Long-transcript fallback | Long-document design | Older architecture; runtime advantage প্রমাণ দরকার | Fallback only |
| 5 | **Word TF–IDF logistic regression** | Sparse ensemble ও safety model | Fast, stable, proven baseline, complementary lexical signal | Shortcut ও weak objective interaction | Low-weight ensemble component |
| 6 | **Small instruction-tuned LLM** | Teacher annotation / distillation | Flexible semantic label | Cost, reproducibility, licence, runtime risk | Optional teacher only |
| 7 | **Large generative LLM classifier** | Direct final predictor | Broad reasoning potential | Slow, costly, difficult calibration | Priority নয় |

ModernBERT একটি bidirectional encoder, যার native context window 8,192 token এবং efficiency/long-context fine-tuning-এর জন্য design করা হয়েছে।[^modernbert] DeBERTa-v3-base compact objective–evidence cross-encoding-এর শক্তিশালী alternative; official model card-এ MIT licence উল্লেখ আছে।[^deberta]

Competition runtime Python 3.12, internet ছাড়া inference, preloaded/local Hugging Face model, six-hour full-submission limit এবং সীমিত weekly submission ব্যবহার করে। Exact model availability আগে verify করতে হবে।[^competition-runtime]





### ৫.২ Recommended master architecture

```text
Raw ordered transcript
        │
        ├── Turn parser
        │      role + timestamp + utterance order
        │
Learning objective
        │
        ├── Sparse retrieval
        │      TF–IDF + mathematical overlap
        │
        ├── Dense retrieval
        │      sentence-transformer embeddings
        │
        └── Cross-encoder reranking
               objective × candidate turn
                        │
                        ▼
          Role- and time-aware evidence pack
          ┌──────────────────────────────┐
          │ student evidence before help │
          │ tutor question / scaffold     │
          │ student evidence after help  │
          │ contradiction / uncertainty  │
          │ final student evidence       │
          └──────────────────────────────┘
                        │
                        ▼
             ModernBERT mastery encoder
                        │
       ┌────────────────┼────────────────┐
       │                │                │
 semantic mastery   contradiction   assistance
      logit             logit          logit
       │                │                │
       └────────────────┼────────────────┘
                        │
          Fold-safe objective prior
          + structured interaction features
                        │
                        ▼
                  Gated fusion head
                        │
          Within-session ranking objective
                        │
                        ▼
              Calibrated probability
                        │
          Blend with sparse TF–IDF model
```
# Upated Main Architecture 

```text
                 RAW ORDERED TRANSCRIPT
                          │
                          ▼
                CANONICAL TURN PARSER
             role + timestamp + true order
                          │
                          ▼
                  LEARNING OBJECTIVE
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
       Sparse Retrieval          Dense Retrieval
 TF-IDF + char/math overlap     Sentence-Transformer
             │                         │
             └────────────┬────────────┘
                          ▼
                  Candidate Pool
                          │
                          ▼
                 CROSS-ENCODER
                    RERANKING
                          │
                          ▼
              OBJECTIVE-SPECIFIC TURNS
                          │
                          ▼
              ROLE + TIME EVIDENCE PACK
      ┌─────────────────────────────────────┐
      │ Student evidence before feedback    │
      │ Tutor question / scaffold           │
      │ Student evidence after feedback     │
      │ Final student evidence              │
      │ Negative / uncertain evidence       │
      └─────────────────────────────────────┘
                          │
                  max 2048 tokens
                          │
                          ▼
                 MODERNBERT-BASE
                          │
                          ▼
                    Mastery Logit
                         z_sem
                          │
               ┌──────────┴──────────┐
               │                     │
               ▼                     ▼
            BCE Loss           Same-session
                               Pairwise Loss
               │                     │
               └──────────┬──────────┘
                          ▼
                    TOTAL LOSS

        L = BCE + λ_pair × PairwiseLoss


               PARALLEL FEATURE BRANCH
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
 Retrieval/confidence   Tutor/help       Temporal/
      features           features        negative
        └─────────────────┼─────────────────┘
                          ▼
                  20–35 STRUCTURED
                       FEATURES
                          │
                          ▼
                Evidence-confidence gate
                          │
                          ▼
     Fold-safe objective prior + semantic logit
                          │
                          ▼
                   SIMPLE FUSION
                          │
                          ▼
                  NEURAL PROBABILITY
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
      ModernBERT branch          TF-IDF Logistic
             │                         │
             └────────────┬────────────┘
                          ▼
                       OOF BLEND
                          │
                          ▼
         Temperature/Platt calibration
               ONLY if OOF improves
                          │
                          ▼
                  FINAL PROBABILITY
```



### ৫.৩ Transformer input structure

প্রথম implementation-এ synthetic summary নয়, actual retrieved utterance ব্যবহার করতে হবে:

```text
[OBJECTIVE]
Compare and order fractions with different denominators.

[STUDENT_EVIDENCE_BEFORE_FEEDBACK]
Student: I think one third is bigger because three is bigger than four.

[TUTOR_CONTEXT]
Tutor: Think about the size of each part. Which fraction has larger pieces?

[STUDENT_EVIDENCE_AFTER_FEEDBACK]
Student: One third has larger pieces than one fourth, so one third is greater.

[FINAL_STUDENT_EVIDENCE]
Student: Three eighths is less than one half because four eighths equals one half.

[NEGATIVE_OR_UNCERTAIN_EVIDENCE]
Student: I am not sure how to compare them.
```

Summarisation প্রথম version-এ বাদ রাখা ভালো, কারণ summary contradiction, uncertainty বা tutor assistance মুছে ফেলতে পারে।

### ৫.৪ Multi-head prediction

Main encoder থেকে কয়েকটি auxiliary head:

| Head | Target |
|---|---|
| Mastery head | Final 0/1 quiz outcome |
| Evidence-support head | Selected student text objective-কে support করে কি না |
| Contradiction head | Evidence objective-এর বিরুদ্ধে কি না |
| Assistance head | Apparent success tutor revelation/heavy scaffold-এর উপর নির্ভর করেছে কি না |
| Pairwise objective head | Same-session correct objective incorrect objective-এর উপরে থাকা উচিত কি না |
| Retrieval-quality head | Selected turns objective cover করে কি না |

Inference-এর জন্য শুধু mastery head বাধ্যতামূলক। Auxiliary head training-এর সময় representation regularise করবে। Weak বা LLM-generated auxiliary label কম loss weight পাবে এবং ablation ছাড়া retain করা যাবে না।

### ৫.৫ Gated prior fusion

Objective prior unconstrainedভাবে concatenate করলে আবার prior dominance হতে পারে। একটি gated formulation:

$$
z_{\text{final}}
=
z_{\text{prior}}
+
g_{\text{evidence}} z_{\text{semantic}}
-
g_{\text{contradiction}} z_{\text{negative}}
-
g_{\text{assistance}} z_{\text{help}}
$$

Gate নির্ভর করবে:

- Evidence coverage
- Retrieval confidence
- Student-vs-tutor source balance
- Contradiction strength
- Assistance level

Meaningful student evidence না থাকলে prior-এর উপর কিছুটা নির্ভর করা যেতে পারে, কিন্তু probability conservative হওয়া উচিত। Strong contradictory evidence থাকলে probability prior-এর অনেক নিচে নামতে পারতে হবে।

### ৫.৬ Hybrid system কেন ভালো

- Sparse model stable lexical pattern ধরে
- Neural model objective–evidence meaning ধরে
- Prior branch objective difficulty ধরে
- Structured branch dialogue form ধরে
- Retrieval branch relevant context বেছে নেয়

Ensemble member শুধু তখনই রাখা হবে যখন OOF residual sufficiently complementary। Bi-encoder retrieval computationally feasible করে; cross-encoder shortlisted evidence jointly পড়ে accuracy বাড়ায়।[^sbert][^cross-encoder]

---

## ৬. Training, Validation এবং Error-analysis Design

Official leaderboard metric Log Loss হওয়ায় primary training objective ordinary binary cross-entropy (BCE) থাকা উচিত। Threshold tuning leaderboard Log Loss improve করে না, কারণ submission-এ hard class নয়—probability জমা দেওয়া হয়। Threshold diagnostic-এর জন্য useful, কিন্তু false positive কমাতে probability estimation এবং objective discrimination উন্নত করতে হবে।[^competition-task]

### ৬.১ Loss function design

Recommended initial objective:

$$
L =
L_{\text{BCE}}
+
\lambda_{\text{pair}}L_{\text{within-session ranking}}
+
\lambda_{\text{sup}}L_{\text{support}}
+
\lambda_{\text{con}}L_{\text{contradiction}}
+
\lambda_{\text{retr}}L_{\text{retrieval}}
$$

Same-session positive ও negative objective pair-এর জন্য:

$$
L_{\text{pair}}
=
\log\left(1+\exp\left[-(z^+ - z^-)\right]\right)
$$

এই loss সরাসরি objective-collapse mechanism target করে। Same-session incorrect objectives সবচেয়ে high-value hard negative, কারণ এগুলো একই student, tutor, session length এবং অনেক shared vocabulary ব্যবহার করে।

Standard BCE মোট loss-এর সবচেয়ে বড় অংশ বহন করবে। Class-weighted BCE default হওয়া উচিত নয়, কারণ এটি effective prior বদলে calibration খারাপ করতে পারে। Focal loss secondary experiment হিসেবে test করা যেতে পারে; কিন্তু recall নয়, OOF Log Loss দিয়ে বিচার করতে হবে।

### ৬.২ Sampling strategy

প্রতিটি training batch-এ controlled mixture থাকবে:

- Ordinary random responses
- Mixed-label sessions
- Same-session positive–negative pairs
- Rare objectives
- Previous generation-এর confident false positives
- সীমিত confident false negatives
- Successful discrimination controls

Oversampling gradient exposure বাড়াতে পারে, কিন্তু artificial batch prevalence যাতে model না শেখে, সে জন্য primary BCE contribution-এ importance correction বা balanced accounting ব্যবহার করতে হবে।

### ৬.৩ Initial hyperparameter range

| Parameter | Initial range |
|---|---|
| Main encoder | ModernBERT-base; DeBERTa-v3-base fallback |
| Maximum evidence tokens | 2,048; 4,096; 8,192 শুধু প্রয়োজন হলে |
| Learning rate | $1\times10^{-5}$ থেকে $3\times10^{-5}$ |
| Weight decay | 0.01–0.05 |
| Effective batch size | 16–32, gradient accumulation সহ |
| Epoch | 2–4 |
| Warm-up | Total update-এর 5–10% |
| Scheduler | Linear অথবা cosine decay |
| Dropout | 0.1–0.2 |
| Pairwise-loss weight | 0.05–0.30 |
| Auxiliary-head total weight | 0.05–0.25 |
| Retrieval shortlist | 8–12 student turns; 4–8 tutor turns |
| Early stopping | Fold Log Loss; patience = 1 evaluation cycle |

এগুলো starting range, claimed optimum নয়। Input pipeline stable না হওয়া পর্যন্ত full five-fold training শুরু করা উচিত নয়। প্রথমে একটি engineering fold-এ correctness, runtime এবং memory benchmark করতে হবে।

### ৬.৪ Freezing strategy

প্রথমে low learning rate দিয়ে full fine-tuning চেষ্টা করা হবে। Training unstable হলে:

1. Lower layers প্রথম 10–20% update freeze
2. তারপর gradual unfreezing
3. Discriminative learning rate প্রয়োজনে ব্যবহার

Permanent heavy freezing এড়িয়ে চলা উচিত, কারণ generic language encoder-কে tutoring-specific objective–evidence reasoning শিখতে হবে। Compute constraint হলে adapter/LoRA-style parameter-efficient tuning fallback হতে পারে, তবে encoder classification performance OOF-এ যাচাই করতে হবে।

### ৬.৫ Validation framework

Primary validation হবে fixed **five-fold session-grouped OOF**। Custom fold assignment response count ও label prevalence balance করবে, কিন্তু একটি session কখনো একাধিক fold-এ যাবে না। একই split manifest সব experiment-এ reuse করতে হবে।

| Validation view | উদ্দেশ্য |
|---|---|
| Five-fold grouped OOF | Primary model selection |
| Mixed-label-session subset | Objective discrimination |
| Rare-objective subset | Common prior-এর বাইরে generalisation |
| Semantic objective-cluster holdout | Related but unseen objective generalisation |
| Duplicate-cluster stress split | Memorisation audit |
| Extreme-length subset | Truncation ও runtime robustness |
| Negative-class subset | False-positive control |
| Subgroup calibration curve | Probability reliability |

Official reference pipeline-ও session grouping অপরিহার্য বলে, কারণ একই session থেকে একাধিক objective response তৈরি হয়।[^reference-analysis]

### ৬.৬ প্রতিটি experiment-এ বাধ্যতামূলক metrics

| Metric | Baseline reference |
|---|---:|
| Overall OOF Log Loss | 0.55546 |
| Fold-wise Log Loss | সব পাঁচটি save করতে হবে |
| Positive-class Log Loss | প্রায় 0.327 |
| Negative-class Log Loss | প্রায় 1.095 |
| False-positive rate at 0.5 | 81.04% |
| High-confidence false-positive rate | 13.26% |
| Mixed-session response Log Loss | প্রায় 0.770 |
| Mixed-session session-mean Log Loss | প্রায় 0.782 |
| Same-session pair accuracy | প্রায় 67.9% |
| Median positive–negative margin | 0.0051 |
| Pair-collapse rate | প্রায় 73.23% |
| Session-collapse rate | প্রায় 74.93% |
| Rare-objective Log Loss | প্রায় 0.610 |
| Objective-macro Log Loss | প্রায় 0.594 |
| Expected calibration error | calibration-এর আগে প্রায় 0.0103 |

শুধু AUROC বাড়লে candidate accept করা যাবে না। Official ranking Log Loss দিয়ে হয়; AUROC reference metric।[^competition-task]

### ৬.৭ Experiment promotion rule

কোনো candidate পরবর্তী stage-এ যাবে যদি:

1. Paired OOF Log Loss কমপক্ষে **0.003** improve করে, অথবা paired bootstrap confidence interval improvement strongly support করে
2. অন্তত ৪টি fold improve বা effectively tie করে
3. Negative-class Log Loss worsen না করে
4. High-confidence false-positive loss worsen না করে
5. Mixed-session median margin improve করে
6. Collapse/reversal কমায়
7. Gain শুধু common objective থেকে না আসে
8. Runtime submission budget-এর মধ্যে থাকে

`0.003` একটি internal engineering gate; guarantee নয়। এর চেয়ে ছোট stable gain ensemble-এ useful হতে পারে যদি residual complementary হয়।

### ৬.৮ Calibration

Calibration discrimination model freeze হওয়ার পরে করতে হবে। Previous result:

- Raw grouped Log Loss: 0.555460
- Calibrated Log Loss: 0.555329
- Improvement: প্রায় 0.00013

এটি খুব ছোট gain, এবং mixed-session/high-confidence FP behaviour কিছু ক্ষেত্রে খারাপ হয়েছে। তাই calibration core solution নয়।

Test করতে হবে:

- Temperature scaling
- Platt scaling
- Conservative probability shrinkage
- Isotonic regression, খুব সতর্কভাবে

Calibrator outer-fold বা OOF framework-এর মধ্যে fit হবে। Model selection-এর একই prediction-এর উপর calibrator fit করলে optimistic result হবে।

### ৬.৯ Ensembling এবং stacking

OOF prediction columns তৈরি হবে:

- Word TF–IDF logistic model
- Fold-safe objective-prior model
- ModernBERT mastery model
- DeBERTa evidence model
- Structured interaction model
- Optional external-pretrained model

প্রথম blend simple non-negative simplex-constrained হবে:

$$
p =
w_1p_{\text{ModernBERT}}
+
w_2p_{\text{TF–IDF}}
+
w_3p_{\text{DeBERTa}}
+
w_4p_{\text{prior}}
$$

Sparse model weight 10–25% একটি search range, predetermined final value নয়। Unconstrained high-dimensional stacking এড়িয়ে চলা উচিত, কারণ 35,072 rows-এ highly correlated model overfit করতে পারে।

### ৬.১০ Error-analysis loop

প্রতিটি meaningful model generation-এর পরে:

```text
OOF predictions
      ↓
Loss decomposition
      ↓
Same-session pair analysis
      ↓
Retrieval inspection
      ↓
Speaker ও temporal evidence audit
      ↓
Manual review sample
      ↓
একটি testable hypothesis
      ↓
Controlled ablation
```

Broad hyperparameter sweep-এর আগে mechanism change identify করতে হবে। প্রতিটি experiment record:

| Field | উদাহরণ |
|---|---|
| Hypothesis | Student-after-feedback evidence tutor-led false positive কমাবে |
| Change | Post-feedback evidence channel যোগ করা |
| Expected metric | Mixed-session negative Log Loss কমবে |
| Primary result | Paired OOF Log Loss delta |
| Mechanism result | Session margin ও collapse delta |
| Risk | Legitimate tutor-supported learning suppress হতে পারে |
| Decision | Retain / reject / rerun |

### ৬.১১ Inference এবং packaging

Final code requirements:

- Python 3.12
- No internet
- Local/preloaded model weights
- Automatic `submission.csv` generation
- Test content বা test aggregate log না করা
- Full runtime six ঘণ্টার মধ্যে
- Smoke test দশ মিনিটের মধ্যে
- Independent test-sample processing

Inference pipeline প্রতিটি session একবার parse করবে এবং session turn embeddings memory-তে cache করবে। তারপর সেই session-এর সব objectives process করবে। এটি rule-compliant, কারণ shared transcript ওই response rows-এর official input; unrelated test sessions থেকে model কিছু শিখছে না।[^competition-runtime]

---

## ৭. Implementation Roadmap, Success Criteria এবং Fallback Plans

Competition deadline source report অনুযায়ী **27 August 2026, 23:59 UTC**। তাই roadmap broad undirected search নয়; representation repair এবং controlled experiments prioritize করবে।[^competition-rules]

### ৭.১ Phase-by-phase roadmap

| Phase | Deliverable | Required experiment gate |
|---|---|---|
| **Data foundation** | Correct turn parser, canonical tables, split manifest, audit report | Exact row/join checks; zero session overlap; reproducible hashes |
| **Rebuilt diagnostics** | True turn-level EDA, duplicate audit, objective catalogue, hard-case table | Previous aggregated retrieval conclusion formally retired |
| **Retrieval baseline** | Sparse+dense objective-to-turn retrieval, manual relevance check | Reviewed evidence-এ strong top-k coverage |
| **Compact semantic model** | DeBERTa/ModernBERT over retrieved evidence | TF–IDF-এর চেয়ে mixed-session ও negative metrics ভালো |
| **Pairwise objective training** | Same-session hard-negative loss | Margin বাড়ে, collapse কমে, overall LL worsen নয় |
| **Role ও temporal channels** | Student-before, tutor-context, student-after, final-evidence separation | Tutor-led/post-correction FP কমে |
| **Prior-gated fusion** | Fold-safe objective prior + semantic override | Prior strength থাকে, objective collapse কমে |
| **External-data experiments** | GSM8K, EssayJudge, FairytaleQA auxiliary trials | Paired OOF gain ছাড়া retain নয় |
| **Optional licensed auxiliaries** | MRBench/SemEval, written confirmation-এর পরে | Licence clearance + ablation evidence |
| **Master ensemble** | Neural semantic + sparse + prior components | Stable OOF gain ও complementary residual |
| **Calibration** | Cross-fitted temperature/Platt scaling | Subgroup regression ছাড়া lower OOF LL |
| **Submission hardening** | Python 3.12 package, smoke/full runtime benchmark | Correct format, no prohibited logs, six ঘণ্টার নিচে |

### ৭.২ Recommended experiment order

External data দিয়ে শুরু করা হবে না। সঠিক order:

```text
Correct evidence units
        ↓
Objective-conditioned evidence selection
        ↓
Semantic support ও contradiction
        ↓
Same-session discrimination
        ↓
Prior-controlled fusion
        ↓
External auxiliary knowledge
        ↓
Ensemble ও calibration
```

Experiment sequence:

1. True turn parser
2. Lexical + dense objective-to-turn retrieval
3. Compact cross-encoder
4. Same-session pairwise loss
5. Student/tutor branch separation
6. Pre/post-feedback temporal channel
7. Fold-safe prior gating
8. External auxiliary pretraining
9. Ensemble
10. Calibration
11. Runtime packaging

এই order cause isolate করে। একসঙ্গে অনেক change করলে improvement কোন mechanism থেকে এসেছে বোঝা যাবে না।

### ৭.৩ Milestone definition

| Milestone | প্রমাণ |
|---|---|
| Retrieval কাজ করছে | Human-reviewed relevant student evidence top-k-তে random/lexical-only-এর চেয়ে অনেক বেশি |
| Objective conditioning improve করছে | Same-session median margin বাড়ে, collapse কমে |
| Positive bias কমছে | Negative-class LL ও confident FP loss কমে |
| Semantic understanding improve করছে | Contradiction/uncertainty ablation expected direction-এ prediction বদলায় |
| Generalisation improve করছে | Fold, rare objective ও mixed session—সবখানে gain |
| External data useful | Identical architecture-এ auxiliary-trained version control-কে beat করে |
| Ensemble useful | Residual correlation কম এবং blended LL improve করে |
| Submission-ready | Offline runtime, memory, licence, reproducibility check pass |

### ৭.৪ Evidence-based target

Leaderboard gain guarantee করা যাবে না। Sensible internal target:

- Grouped OOF Log Loss 0.55546 থেকে original holdout 0.5455-এর দিকে বা নিচে নামানো
- Negative-class Log Loss materially কমানো
- Same-session collapse কমানো
- High-confidence false-positive loss কমানো

Scientific success-এর minimum direction:

| Outcome | Required direction |
|---|---|
| Overall grouped OOF Log Loss | কমতে হবে |
| Negative-class Log Loss | উল্লেখযোগ্যভাবে কমতে হবে |
| High-confidence FP loss share | কমতে হবে |
| Same-session median margin | বাড়তে হবে |
| Pair/session collapse | কমতে হবে |
| Rare-objective Log Loss | কমবে বা stable থাকবে |
| Positive-class Log Loss | বড় degradation নয় |
| Fold dispersion | কমতে হবে |
| Public/private generalisation | আরও consistent হতে হবে |

Objective prior exploit করে overall LL সামান্য কমলেও mixed-session collapse unchanged থাকলে সেটিকে final master model বলা যাবে না। Competition write-up transcript-grounded educational insight, generalisability এবং methodological rigour মূল্যায়ন করে।[^competition-task]

### ৭.৫ Principal risks এবং fallback plan

| Risk | Early warning | Mitigation | Fallback |
|---|---|---|---|
| Retrieval crucial evidence miss করে | Relevant turn top-k-তে নেই | Hybrid sparse+dense; neighbours ও final segment যোগ | Hierarchical sliding-window encoder |
| Long-context model খুব ধীর | Runtime projection budget ছাড়ায় | Token budget কমানো; session encoding cache | Retrieved chunk-এর উপর DeBERTa |
| Pairwise loss calibration খারাপ করে | Margin বাড়ে, LL খারাপ | Auxiliary weight কমানো; BCE dominate | Pair loss বাদ, pair-balanced batch |
| Positive bias থেকে যায় | Negative LL high | Strong contradiction head ও prior gating | OOF calibration-এর পরে conservative shrinkage |
| Model negatives overcorrect করে | Positive loss/FNR sharply বাড়ে | Random positives preserve, FNR monitor | TF–IDF/prior blend |
| Objective prior dominate করে | Semantic ablation-এ prediction বদলায় না | Prior dropout, evidence override regulariser | Prior branch weight কমানো |
| External data negative transfer দেয় | Main OOF worsen | Task weight কমানো, adapter-only transfer | External data discard |
| Licence ambiguity | Written confirmation পাওয়া যায় না | Dataset final weights থেকে বাদ | Permissive dataset only |
| LLM annotation inconsistent | Repeat prompt agreement low | Deterministic decoding, rubric refine, human audit | Rule-based/supervised auxiliary labels |
| Duplicate leakage CV inflate করে | Duplicate-cluster split অনেক খারাপ | Duplicate cluster grouping | Conservative model selection |
| Rare objective দুর্বল থাকে | Macro LL high | Semantic objective clustering ও shrinkage prior | Global prior + uncertainty shrinkage |
| Calibration unstable | Fold calibrator disagreement | Single temperature বা no calibration | Global prior-এর দিকে mild blend |
| ModernBERT runtime-এ unavailable | Model preload/package fail | Package weights if allowed | DeBERTa-v3-base / available encoder |
| Full ensemble six ঘণ্টা ছাড়ায় | Smoke-test scaling high | Ensemble distillation | Compact semantic model + TF–IDF |

---

## ৮. Final Recommendation

Final master model একটি বড় flat classifier হবে না। এটি হবে:

> **Objective-conditioned hierarchical evidence model**

Core components:

1. Role ও timestamp-preserving correct turn parser
2. Objective-relevant moment-এর hybrid sparse/dense retrieval
3. Selected student, tutor ও post-feedback evidence-এর উপর ModernBERT-base mastery encoder
4. Explicit support, contradiction ও assistance representation
5. Controlled gate-এর মাধ্যমে fold-safe objective prior
6. Same-session hard-negative training
7. Low-weight TF–IDF ensemble component
8. Discrimination improve হওয়ার পরে OOF-only calibration
9. Permissively licensed auxiliary pretraining—শুধু controlled validation-এ লাভ হলে
10. Python 3.12 offline packaging এবং independent test processing

Expected improvement-এর source “আরও বেশি text” বা “আরও বেশি tuning” নয়। প্রয়োজন একটি specific structural change:

> **প্রতিটি learning objective-এর জন্য সঠিক মুহূর্তগুলো retrieve করতে হবে; student evidence-কে tutor assistance থেকে আলাদা করতে হবে; support ও contradiction বুঝতে হবে; এবং একই conversation-এর correct ও incorrect objective-কে model-কে বাধ্যতামূলকভাবে আলাদা করতে শেখাতে হবে।**

এই architecture baseline-এর observed সমস্যাগুলোকে সরাসরি target করে:

- False-positive bias
- Transcript dominance
- Lexical shortcut
- Objective collapse
- Weak negative semantics
- Rare-objective generalisation
- Complex mixed-session failure

একই সঙ্গে baseline-এর শক্তিশালী অংশ—TF–IDF lexical signal, grouped validation এবং objective prior—নিয়ন্ত্রিতভাবে retain করে।

---

## ৯. এক নজরে Step-by-step Execution Order

```text
Step 1  → Project freeze, environment pin, split manifest
Step 2  → True turn parser এবং canonical data tables
Step 3  → Advanced turn/session/objective/pair EDA
Step 4  → Duplicate, noise, label consistency ও shortcut audit
Step 5  → Manual evidence review এবং retrieval gold sample
Step 6  → Sparse + dense turn retrieval baseline
Step 7  → Cross-encoder retrieval reranker
Step 8  → ModernBERT/DeBERTa objective-conditioned classifier
Step 9  → Same-session hard-negative pairwise training
Step 10 → Speaker-role ও pre/post-feedback channels
Step 11 → Fold-safe objective prior + gated fusion
Step 12 → External auxiliary-data experiments
Step 13 → OOF ensemble ও mechanism-level error analysis
Step 14 → Cross-fitted calibration
Step 15 → Python 3.12 offline packaging ও submission benchmark
```

---

## ১০. Final Decision Rule

একটি model-কে “Master Model” বলা হবে শুধু তখনই, যখন নিচের সবগুলো evidence থাকবে:

- Baseline-এর তুলনায় lower grouped OOF Log Loss
- Stable fold-wise improvement
- Lower negative-class Log Loss
- Lower confident false-positive burden
- Higher same-session objective margin
- Lower collapse ও reversal
- Rare objectives-এ stable বা improved performance
- Positive-class performance-এর বড় ক্ষতি নেই
- No session leakage
- No global target leakage
- Runtime এবং licensing compliance
- Reproducible preprocessing ও inference
- Controlled ablation দ্বারা architecture-এর লাভ explainable

> **Improvement must be demonstrated, not assumed.**

---

## সূত্র ও রেফারেন্স

[^competition-task]: K-12 AI Infrastructure Program, **Trace the Ace — Tutoring Outcomes Competition**, task description ও evaluation documentation: <https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/4/>

[^competition-rules]: K-12 AI Infrastructure Program, competition rules, external-resource policy ও test-processing restrictions: <https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/>

[^competition-runtime]: K-12 AI Infrastructure Program, submission environment ও runtime guidance: <https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/6/>

[^reference-analysis]: DrivenData, **Productive math talk: a simple reference solution for Trace the Ace**: <https://drivendata.co/blog/productive-math-talk-reference>

[^sbert]: Reimers & Gurevych, **Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks**: <https://arxiv.org/abs/1908.10084>

[^cross-encoder]: SentenceTransformers documentation, **CrossEncoder usage and model reference**: <https://www.sbert.net/docs/cross_encoder/usage/usage.html>

[^simcse]: Gao, Yao & Chen, **SimCSE: Simple Contrastive Learning of Sentence Embeddings**: <https://huggingface.co/papers/2104.08821>

[^modernbert]: Warner et al., **Smarter, Better, Faster, Longer: A Modern Bidirectional Encoder for Fast, Memory Efficient, and Long Context Finetuning and Inference**: <https://arxiv.org/abs/2412.13663>

[^deberta]: Microsoft, **DeBERTa-v3-base model card**: <https://huggingface.co/microsoft/deberta-v3-base>

[^bridge]: K-12 AI Infrastructure Program, **Bridge dataset**: <https://platform.k12-ai-infrastructure.org/datasets/7/bridge/version/7/>

[^drawedumath]: K-12 AI Infrastructure Program, **DrawEduMath dataset**: <https://platform.k12-ai-infrastructure.org/datasets/8/drawedumath/version/8/>

[^essayjudge]: K-12 AI Infrastructure Program, **EssayJudge dataset**: <https://platform.k12-ai-infrastructure.org/datasets/6/essayjudge/version/6/>

[^fairytaleqa]: K-12 AI Infrastructure Program, **FairytaleQA dataset**: <https://platform.k12-ai-infrastructure.org/datasets/10/fairytaleqa/version/10/>

[^gsm8k]: K-12 AI Infrastructure Program, **Grade School Math (GSM8K) dataset**: <https://platform.k12-ai-infrastructure.org/datasets/1/gsm8k/version/1/>

[^mrbench]: K-12 AI Infrastructure Program, **MRBench dataset**: <https://platform.k12-ai-infrastructure.org/datasets/3/mrbench/version/3/>

[^sciq]: K-12 AI Infrastructure Program, **SciQ dataset**: <https://platform.k12-ai-infrastructure.org/datasets/4/sciq/version/4/>

[^semeval]: K-12 AI Infrastructure Program, **SemEval short-answer dataset**: <https://platform.k12-ai-infrastructure.org/datasets/11/semeval/version/11/>

[^talkmoves]: K-12 AI Infrastructure Program, **TalkMoves dataset**: <https://platform.k12-ai-infrastructure.org/datasets/9/talkmoves/version/9/>

[^external-data-rules]: K-12 AI Infrastructure Program, external dataset declarations ও licence requirements: <https://platform.k12-ai-infrastructure.org/>





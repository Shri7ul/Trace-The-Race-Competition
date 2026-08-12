# Trace The Ace — Project Progress & Verified Outputs So Far

## 0. Current Status — Executive Summary

এখন পর্যন্ত project-এর **data foundation সম্পূর্ণভাবে তৈরি, audited এবং frozen** হয়েছে। এরপর retrieval phase-এর **R0 — Retrieval Input Builder** শুরু হয়েছে এবং canonical data successfully discover ও schema/shape audit করা হয়েছে।

### Current pipeline status

```text
Environment / Paths
        ↓
Data Inventory
        ↓
Turn Parser
        ↓
Data Integrity
        ↓
Canonical Data Foundation
        ↓
R0 Retrieval Input Builder  ← CURRENT STAGE
        ↓
R1 Sparse Retrieval          ← NOT STARTED
        ↓
R2 Dense Retrieval           ← NOT STARTED
        ↓
R3 Candidate Union           ← NOT STARTED
        ↓
Cross-Encoder Reranking      ← NOT STARTED
        ↓
Evidence Pack
        ↓
ModernBERT Mastery Model
        ↓
Structured Branch + Prior
        ↓
OOF Blend + Calibration
        ↓
Final Probability
```

**Important:** `R0` এখনো পুরোপুরি শেষ হয়নি। `04_R0_retrieval_input_builder.ipynb`-এ canonical discovery এবং schema/shape validation সম্পন্ন হয়েছে, কিন্তু final retrieval artifacts যেমন `retrieval_queries.parquet`, `session_turn_index.parquet`, এবং `objective_catalogue.parquet` এখনো এই notebook-এর executed output হিসেবে তৈরি হয়নি। তাই R1 শুরু করা হয়নি। 

---

# 1. Environment & Project Setup

## Notebook

```text
00_environment_and_paths.ipynb
```

এই notebook-এর কাজ ছিল পুরো project-এর authoritative paths, input files, frozen fold manifest এবং source lineage establish করা।

### Environment

```text
Python : 3.10.20
OS     : Windows 10
```

Resolved project:

```text
PROJECT_ROOT
D:\Competition\Trace-the-race-local

DATA_ROOT
D:\Competition\Trace-the-race-local\Dataset

TRANSCRIPT_ROOT
D:\Competition\Trace-the-race-local\Dataset\train_transcripts

NOTEBOOK_ROOT
D:\Competition\Trace-the-race-local\Notebooks

SCRATCH_OUTPUT_ROOT
D:\Competition\Trace-the-race-local\scratch_mastery_outputs
```

### Authoritative training inputs

```text
train_features_TMQTWsB.csv
train_labels_44ujmj2.csv
```

Feature schema:

```text
response_id
session_id
learning_objective_id
learning_objective
```

Label schema:

```text
response_id
is_correct
```

### Data population

```text
Responses       : 35,072
Sessions        : 22,821
Objectives      : 398
Positive labels : 24,637
Negative labels : 10,435
Positive rate   : 70.2469%
```

Feature/label population perfectly aligned:

```text
Feature IDs : 35,072
Label IDs   : 35,072

Feature-only : 0
Label-only   : 0
```

Objective consistency:

```text
Objective IDs      : 398
Inconsistent IDs   : 0
```

### Transcript discovery

```text
Transcript files discovered: 22,821
```

Representative transcript schema successfully validated.

### Source fingerprinting

All 22,821 transcript files were fingerprinted.

Transcript directory SHA256:

```text
3f563b9911cd2f2e4d01dd5a457509ceaac6eb31ae880148034d7b2ca89402df
```

Feature and label files were also SHA256 fingerprinted.

### Frozen 5-fold session-grouped manifest

Existing fold manifest was preserved rather than regenerated.

```text
Rows    : 35,072
Sessions: 22,821
Folds   : 5
```

Fold distribution:

| Fold | Responses | Sessions | Positives | Positive Rate |
| ---: | --------: | -------: | --------: | ------------: |
|    0 |     6,958 |    4,539 |     4,879 |      0.701207 |
|    1 |     7,050 |    4,557 |     4,958 |      0.703262 |
|    2 |     7,023 |    4,560 |     4,915 |      0.699843 |
|    3 |     7,081 |    4,594 |     4,978 |      0.703008 |
|    4 |     6,960 |    4,571 |     4,907 |      0.705029 |

Session leakage audit:

```text
Sessions checked : 22,821
Max fold count   : 1
Session leakage  : NONE
```

### Final setup gate

```text
data_paths_ready           = True
feature_label_schema_ready = True
frozen_folds_ready         = True
transcript_source_ready    = True

SETUP_READY = True
```

**Status: PASS**

---

# 2. Data Inventory

## Notebook

```text
01_data_inventory.ipynb
```

এই notebook authoritative response population, objective catalogue, transcript coverage এবং inventory contract তৈরি করেছে।

### Main outputs

```text
responses_base.parquet
data_contract.json
inventory_manifest.json
```

Location:

```text
scratch_mastery_outputs/
└── 01_data_foundation/
    └── 01_inventory/
        └── responses_base.parquet
```

### Final inventory

```text
Responses              : 35,072
Sessions               : 22,821
Current objectives     : 398
Transcript sessions    : 22,821
Response rows matched  : 35,072
Cross-fold sessions    : 0
Final blockers         : 0
Warnings               : 2
```

Inventory gate:

```text
FINAL_GATE_PASS = True
INVENTORY_READY = True
```

### Important result

Training response population এবং transcript population-এর মধ্যে full session coverage পাওয়া গেছে:

```text
35,072 responses
        ↓
22,821 labelled sessions
        ↓
22,821 transcript files
```

অর্থাৎ কোনো labelled session transcript coverage থেকে বাদ যায়নি।

**Status: PASS**



---

# 3. Raw Transcript Ingestion & Turn Reconstruction

## Notebook

```text
02_turn_parser.ipynb
```

এটাই Phase-1-এর সবচেয়ে বড় engineering component।

Goal ছিল raw transcript files থেকে **trusted, ordered, provenance-preserving turn representation** তৈরি করা।

---

## 3.1 Full Corpus Size

পুরো corpus:

```text
Sessions : 22,821
Turns    : 6,139,854
```

Full stream parse:

```text
22,821 / 22,821 files
6,139,854 turns
```

---

# 3.2 Raw Ingestion Validation

Synthetic এবং real ingestion tests সম্পন্ন হয়েছে।

```text
Passed ingestion tests : 10 / 10
Policy failures        : 0
Test failures          : 0
Smoke failures         : 0

INGESTION READY = True
```

---

# 3.3 Raw Format Discovery

Full corpus format discovery:

```text
Sessions          : 22,821
Required failures : 0

FORMAT READY = True
```

---

# 3.4 Parser Schema Freeze

Parser schema successfully frozen:

```text
Schema version : 1.0
Schema failures: 0

SCHEMA READY = True
```

Final schemas:

```text
Turn schema    : 52 fields
Session schema: 31 fields
```

---

# 3.5 Raw Row Reconstruction

Raw reconstruction tests:

```text
Row failures    : 0
Schema failures : 0
Roundtrip fails : 0
Index failures  : 0
Hash failures   : 0

RAW ROW READY = True
```

এটার অর্থ raw source থেকে reconstructed representation-এ:

* row conservation ঠিক আছে
* schema পরিবর্তন হয়নি
* source index preserve হয়েছে
* hash consistency ঠিক আছে
* round-trip reconstruction সফল

---

# 3.6 Structural Audit

Full corpus structural audit:

```text
Gate failures    : 0
STRUCTURAL READY : True
```

---

# 3.7 Text Normalization

Math-safe normalization তৈরি হয়েছে।

```text
Math failures : 0
TEXT READY    : True
```

Original content delete না করে normalized representation আলাদা রাখা হয়েছে।

---

# 3.8 Role Canonicalization

Speaker roles canonicalized হয়েছে।

```text
Real failures : 0
ROLE READY    : True
```

---

# 3.9 Utterance ID Parsing

```text
Contiguous sessions : 22,821 / 22,821
ID PARSER READY      : True
```

---

# 3.10 Timestamp Parsing

Full timestamp audit সম্পন্ন:

```text
TIMESTAMP READY = True
```

---

# 3.11 Deterministic Ordering

Ordered transcript retrieval-এর জন্য সবচেয়ে গুরুত্বপূর্ণ অংশগুলোর একটি।

Final ordering policy:

```text
Certified sessions : 22,821 / 22,821
ORDERING READY      : True
```

Ordering policy label-blind এবং deterministic।

---

# 3.12 Ordering Conflict Audit

```text
Sessions               : 22,821
Timestamp-tie sessions : 22,795
Fallback sessions      : 0
Rollover sessions      : 0
Ambiguous sessions     : 0

CONFLICT AUDIT READY = True
```

অর্থাৎ timestamp tie প্রচুর থাকলেও fallback/ambiguous ordering-এর প্রয়োজন হয়নি।

---

# 3.13 Physical & Logical Identity

Identity algorithm:

```text
SHA256
```

Expected fallback rows:

```text
0
```

Final:

```text
IDENTITY READY = True
```

---

# 3.14 Structural Turn Metadata

```text
Expected sessions : 22,821
Ambiguous         : 0
Fallback          : 0
Rollover          : 0

STRUCTURAL READY = True
```

---

# 3.15 Integrated Parser

```text
Integrated parser version : 1.0
Turn schema               : 52 / 52
Session schema             : 31 / 31
Real E2E sessions          : 8 / 8
Order-sensitive hashing    : True

INTEGRATED PARSER READY = True
```

---

# 3.16 Production Parse

Production parse:

```text
Expected sessions : 22,821
Expected turns    : 6,139,854

Turn schema       : 52 fields
Session schema    : 31 fields
Batch size        : 250 sessions
```

Full production parse completed:

```text
22,821 / 22,821 sessions
6,139,854 / 6,139,854 turns
92 parts
```

Approximate parse duration recorded:

```text
~13.9 minutes
```

---

# 3.17 Candidate Artifact Certification

Final candidate artifacts:

```text
turns_candidate.parquet
sessions_candidate.parquet
```

Final certification snapshot:

```text
Turn artifact rows           : 6,139,854
Session artifact rows        : 22,821
Turn artifact SHA256 stable  : True
Upstream gates passed        : 4/4
Certification snapshot ready : True
```

Final parser gate:

```text
Candidate turns  : 6,139,854 / 6,139,854
Candidate sessions: 22,821 / 22,821
Turn schema      : 52 / 52
Session schema   : 31 / 31
Hash verified    : True
Final failed checks: 0

PARSER READY FOR INTEGRITY = True
```

**Important distinction:** এগুলো তখনও `candidate` artifact ছিল; canonical হওয়ার জন্য `03_data_integrity.ipynb`-এর final gate প্রয়োজন ছিল। 

---

# 4. Canonical Data Integrity & Freeze

## Notebook

```text
03_data_integrity.ipynb
```

এটাই Phase-1-এর final certification layer।

এখানে মূলত:

```text
Source identity
Schema identity
Entity keys
Relationships
Structural integrity
Duplicate/objective integrity
Fold leakage
Traceability
Serialization
Inference symmetry
Canonical publication
```

সব audit করা হয়েছে।

---

## 4.1 Integrity Section Gates

সবগুলো section ready হয়েছে:

```text
INTEGRITY_BOOTSTRAP_READY       = True
ENTITY_KEY_INTEGRITY_READY      = True
RELATIONAL_INTEGRITY_READY      = True
STRUCTURAL_INTEGRITY_READY      = True
DUPLICATE_OBJECTIVE_INTEGRITY_READY = True
FOLD_LEAKAGE_INTEGRITY_READY    = True
TRACEABILITY_SYMMETRY_READY     = True
CANONICAL_BUILD_READY           = True
CANONICAL_PUBLICATION_READY     = True
```

---

# 4.2 Final 17 Hard Gates

| Gate | Requirement                                   | Status |
| ---- | --------------------------------------------- | ------ |
| G01  | Source/schema identity valid                  | PASS   |
| G02  | Feature-label population aligned              | PASS   |
| G03  | `response_id` unique                          | PASS   |
| G04  | Target valid                                  | PASS   |
| G05  | Objective population deterministic            | PASS   |
| G06  | Labelled-session transcript coverage          | PASS   |
| G07  | Every response assigned to one frozen fold    | PASS   |
| G08  | Zero session cross-fold overlap               | PASS   |
| G09  | Parser deterministic                          | PASS   |
| G10  | Turn identity unique                          | PASS   |
| G11  | Within-session turn sequence contiguous       | PASS   |
| G12  | Response → Session → Turn relationships valid | PASS   |
| G13  | No silent many-to-many expansion              | PASS   |
| G14  | Raw → canonical provenance valid              | PASS   |
| G15  | Serialization round-trip valid                | PASS   |
| G16  | Parser independent of target/test aggregates  | PASS   |
| G17  | Canonical files published only after audit    | PASS   |

```text
Hard gates passed : 17 / 17
```

---

# 4.3 Canonical Dataset Foundation

Final canonical population:

```text
responses : 35,072
sessions  : 22,821
turns     : 6,139,854
objectives: 398
```

Canonical artifacts:

```text
scratch_mastery_outputs/
└── 01_data_foundation/
    └── 03_integrity/
        └── canonical/
            ├── responses.parquet
            ├── turns.parquet
            ├── sessions.parquet
            └── objectives.parquet
```

Final:

```text
Canonical publication ready : True
Audit workbook ready         : True
Phase manifest ready         : True
Phase gate file ready        : True

PHASE 1 FOUNDATION READY = True
```

**Phase 1 is frozen.**



---

# 5. Important Data-quality Findings Retained for Downstream Work

Phase-1 পুরোপুরি clean হলেও কিছু **warnings/information** intentionally retain করা হয়েছে; এগুলো data deletion বা repair trigger হিসেবে ব্যবহার করা হয়নি।

```text
UNCLEAR_MARKER_PRESENT
Count: 180,538

VERY_LONG_UTTERANCE
Count: 474

CONSECUTIVE_EXACT_CONTENT
Count: 58,061
```

এছাড়া inventory stage-এ:

```text
Warnings: 2
Blockers: 0
```

এগুলো downstream retrieval/temporal/evidence analysis-এর জন্য diagnostic context হিসেবে রাখা হয়েছে।

---

# 6. Canonical Dataset Responsibilities

এখন canonical layer-এর role fixed:

| Dataset              | Role                                     |
| -------------------- | ---------------------------------------- |
| `responses.parquet`  | Response/query driver                    |
| `objectives.parquet` | Canonical objective catalogue/query text |
| `turns.parquet`      | **Actual retrieval corpus**              |
| `sessions.parquet`   | Session-level structural metadata        |

Retrieval architecture:

```text
responses
    │
    ├── session_id ───────► sessions
    │                          │
    │                          ▼
    │                       session metadata
    │
    └── objective_uid ────► objectives
                               │
                               ▼
                         objective query

session_id
    │
    ▼
turns
    │
    ▼
session-local evidence search
```

সবচেয়ে গুরুত্বপূর্ণ rule:

```text
Objective
    ×
ONLY turns from the same session
```

Global:

```text
35,072 responses × 6,139,854 turns
```

করা হবে না। 

---

# 7. Retrieval Architecture Design

## Source document

```text
retrival.md
```

এখানে retrieval-এর data relationship এবং R0 → R1 → R2 → R3 design স্থির করা হয়েছে। 

---

## R0 — Retrieval Input Builder

### Planned notebook

```text
04_R0_retrieval_input_builder.ipynb
```

Expected artifacts:

```text
02_retrieval/
└── R0_input/
    ├── retrieval_queries.parquet
    ├── session_turn_index.parquet
    ├── objective_catalogue.parquet
    └── r0_manifest.json
```

R0-এর rule:

```text
target ❌
```

Retrieval input label-blind থাকবে।

---

# 8. R0 — What Has Actually Been Completed

## Notebook

```text
04_R0_retrieval_input_builder.ipynb
```

**এই notebook এখন পর্যন্ত 2টি executed cell নিয়ে canonical discovery + schema/shape audit করেছে।**

### Cell 1 — Canonical discovery

Successfully found:

```text
responses.parquet
turns.parquet
sessions.parquet
objectives.parquet
```

Status:

```text
STATUS: CANONICAL_ARTIFACTS_FOUND
R0_CANONICAL_DISCOVERY_READY = True
```

---

# 9. R0 Canonical Shapes

### `responses.parquet`

```text
Shape: (35,072, 7)
```

Columns:

```text
response_id
session_id
objective_id_raw
objective_raw
objective_uid
target
fold
```

---

### `turns.parquet`

```text
Shape: (6,139,854, 52)
```

Important fields include:

```text
session_id
turn_uid
source_row_uid
turn_index
role
content_raw
text_norm
timestamp
timestamp_order_value
ordering_method
ordering_confidence
relative_turn_position
previous_role
next_role
speaker_switch
time_since_previous_turn
elapsed_from_session_start
is_first_turn
is_last_turn
...
```

---

### `sessions.parquet`

```text
Shape: (22,821, 33)
```

Important fields include:

```text
session_id
n_turns
n_student_turns
n_tutor_turns
n_background_turns
duration_seconds
ordering_method
ordering_confidence
timestamp_tie_count
ambiguous_order_flag
raw_transcript_hash
normalized_transcript_hash
...
```

---

### `objectives.parquet`

```text
Shape: (398, 5)
```

Columns:

```text
objective_uid
objective_raw
objective_safe_norm
response_count
session_count
```

No nulls were reported in the relevant canonical objective fields.

---

# 10. R0 — Current Exact Status

### Completed

```text
Canonical artifact discovery       ✅
Canonical path verification        ✅
Response schema/shape audit        ✅
Turn schema/shape audit            ✅
Session schema/shape audit         ✅
Objective schema/shape audit       ✅
Canonical source-of-truth confirmed ✅
```

### Not yet completed in executed notebook

```text
retrieval_queries.parquet          ⏳
session_turn_index.parquet         ⏳
objective_catalogue.parquet        ⏳
r0_manifest.json                   ⏳
R0 final freeze gate               ⏳
```

Therefore:

```text
R0_CANONICAL_DISCOVERY_READY = TRUE

R0_COMPLETE = FALSE
R0_FROZEN   = FALSE
```

**এই distinctionটা important।**

R0-এর design document-এ Cell 1–8 পর্যন্ত planned implementation আছে, কিন্তু বর্তমানে uploaded/executed `04_R0_retrieval_input_builder.ipynb`-এ canonical discovery ও schema audit পর্যন্ত execution evidence আছে। 

---

# 11. What We Have NOT Done Yet

এখন পর্যন্ত নিচের কোনো retrieval/model stage productionভাবে complete হয়নি:

```text
05_R1_sparse_retrieval.ipynb
06_R2_dense_retrieval.ipynb
07_R3_candidate_union.ipynb
08_cross_encoder_reranking.ipynb
```

অর্থাৎ এখনো:

```text
TF-IDF retrieval                  ❌
Character/math retrieval          ❌
Dense embedding retrieval        ❌
Candidate union                   ❌
Cross-encoder reranking           ❌
Evidence pack generation          ❌
ModernBERT training               ❌
Same-session pairwise training    ❌
Structured fusion                ❌
Objective prior fusion            ❌
OOF neural prediction             ❌
Neural + TF-IDF blend             ❌
Calibration                       ❌
Final submission model            ❌
```

এগুলো **architecture/roadmap-এ designed**, কিন্তু executed results হিসেবে claim করা যাবে না। 

---

# 12. Previous Baseline Work — What We Already Learned

Master architecture বানানোর আগে baseline analysis থেকে কয়েকটি গুরুত্বপূর্ণ result establish করা হয়েছিল।

Baseline dataset:

```text
Responses : 35,072
Sessions  : 22,821
Positive rate: 70.25%
```

Recorded baseline metrics:

| Model / Evaluation          |   Log Loss |
| --------------------------- | ---------: |
| Constant prior              |     0.5986 |
| Structured model            |    ~0.5924 |
| Word TF-IDF Logistic        | **0.5455** |
| Character TF-IDF Logistic   |     0.5557 |
| Tuned Word + Character      |     0.5482 |
| 5-fold session-grouped OOF  |    0.55546 |
| Recorded public leaderboard |     0.6163 |

Baseline diagnosis থেকে মূল সমস্যা পাওয়া গেছে:

```text
Whole transcript
       ↓
General session impression
       ↓
Objective-specific discrimination দুর্বল
```

বিশেষ করে mixed-label sessions-এ objective-specific separation দুর্বল ছিল।

Recorded diagnostics:

```text
Mixed-label sessions       : 3,207
Same-session positive/negative pairs : 5,323
Median same-session margin : ~0.0051
Session-collapse rate      : ~74.93%
Pairwise reversal rate     : ~32.07%
```

এগুলো থেকেই retrieval-first architecture-এর প্রয়োজনীয়তা এসেছে। 

---

# 13. Why We Changed the Architecture

Baseline model:

```text
OBJECTIVE
    +
FULL TRANSCRIPT
    ↓
Classifier
```

সমস্যা:

```text
General session quality
        +
Objective prior
        ↓
Prediction
```

নতুন architecture:

```text
OBJECTIVE
    ↓
Find relevant turns
    ↓
Separate student/tutor evidence
    ↓
Preserve temporal order
    ↓
Understand support / contradiction
    ↓
Same-session objective comparison
    ↓
Mastery probability
```

Core principle:

> **Objective-specific evidence > general session impression**



---

# 14. Planned Retrieval Pipeline After R0

R0 pass করার পর:

## R1 — Sparse Retrieval

Notebook:

```text
05_R1_sparse_retrieval.ipynb
```

Planned:

```text
Objective
    ↓
TF-IDF
+
character overlap
+
mathematical overlap
    ↓
same-session turns only
    ↓
Top-K
```

Output:

```text
sparse_candidates.parquet
sparse_audit.parquet
tfidf_artifacts/
r1_manifest.json
```

Full objective × turn table save করা হবে না। শুধু shortlisted candidates রাখা হবে। 

---

# 15. R2 — Dense Retrieval

Notebook:

```text
06_R2_dense_retrieval.ipynb
```

Planned:

```text
Objective
    ↓
Sentence Transformer
    ↓
Objective embedding

Turn
    ↓
Sentence Transformer
    ↓
Turn embedding

Objective embedding
        ×
same-session turn embeddings
        ↓
Cosine similarity
        ↓
Top-K
```

Output:

```text
objective_embeddings/
turn_embeddings/
dense_candidates.parquet
dense_audit.parquet
r2_manifest.json
```

---

# 16. R3 — Candidate Union

Notebook:

```text
07_R3_candidate_union.ipynb
```

Planned:

```text
Sparse Top-K
     +
Dense Top-K
     ↓
Deduplicate
     ↓
Candidate Union
```

Output fields:

```text
response_id
session_id
objective_uid
turn_uid
role
turn_index

sparse_score
sparse_rank

dense_score
dense_rank

selected_sparse
selected_dense
candidate_union
```

---

# 17. Cross-Encoder Reranking

Notebook:

```text
08_cross_encoder_reranking.ipynb
```

Planned:

```text
Objective
    +
Candidate Turn
       ↓
Cross-Encoder
       ↓
Relevance Score
       ↓
Rerank
       ↓
Objective-specific evidence
```

Expected output:

```text
reranked_candidates.parquet
evidence_candidates.parquet
reranking_audit.parquet
cross_encoder_manifest.json
```

তারপর retrieval phase freeze হবে।

---

# 18. Master Model After Retrieval

Retrieval complete হলে architecture হবে:

```text
Objective-specific evidence
            ↓
Role + Time Evidence Pack
            ↓
max 2048 tokens
            ↓
ModernBERT-base
            ↓
Semantic Mastery Logit
            ↓
BCE + Same-session Pairwise Loss
```

Parallel branch:

```text
Retrieval confidence
+
Tutor/student features
+
Temporal/negative features
        ↓
20–35 structured features
        ↓
Evidence-confidence gate
        ↓
Fold-safe objective prior
        ↓
Fusion
```

Final:

```text
Neural probability
       +
TF-IDF Logistic
       ↓
OOF Blend
       ↓
Optional Calibration
       ↓
Final Probability
```



---

# 19. Current Project Artifact Tree

এখন পর্যন্ত logical project structure:

```text
Trace-the-race-local/
│
├── Dataset/
│   ├── train_features_TMQTWsB.csv
│   ├── train_labels_44ujmj2.csv
│   └── train_transcripts/
│
├── Notebooks/
│   ├── 00_environment_and_paths.ipynb
│   ├── 01_data_inventory.ipynb
│   ├── 02_turn_parser.ipynb
│   ├── 03_data_integrity.ipynb
│   ├── 04_R0_retrieval_input_builder.ipynb
│   └── dataset_check.ipynb
│
└── scratch_mastery_outputs/
    │
    ├── 00_project_setup/
    │   ├── path_registry.json
    │   ├── setup_summary.json
    │   ├── source_fingerprints.json
    │   └── frozen_fold_manifest.parquet
    │
    └── 01_data_foundation/
        │
        ├── 01_inventory/
        │   └── responses_base.parquet
        │
        ├── 02_turn_parser/
        │   ├── turns_candidate.parquet
        │   ├── sessions_candidate.parquet
        │   └── parser artifacts/manifests
        │
        └── 03_integrity/
            ├── canonical/
            │   ├── responses.parquet
            │   ├── turns.parquet
            │   ├── sessions.parquet
            │   └── objectives.parquet
            │
            ├── phase1_data_foundation_audit.xlsx
            ├── phase1_manifest.json
            └── phase1_gate.json
```

Retrieval outputs এখনো এই tree-তে completed stage হিসেবে ধরা যাবে না।

---

# 20. Notebook Status Board

| Notebook                              | Purpose                                          | Status                   |
| ------------------------------------- | ------------------------------------------------ | ------------------------ |
| `00_environment_and_paths.ipynb`      | Environment, paths, fingerprints, frozen folds   | ✅ **PASS**               |
| `01_data_inventory.ipynb`             | Response/session/objective inventory + contracts | ✅ **PASS**               |
| `02_turn_parser.ipynb`                | Raw → ordered canonical candidate turns          | ✅ **PASS**               |
| `03_data_integrity.ipynb`             | Full integrity + canonical publication           | ✅ **PASS — 17/17 gates** |
| `04_R0_retrieval_input_builder.ipynb` | Canonical retrieval input discovery/audit        | 🟡 **IN PROGRESS**       |
| `05_R1_sparse_retrieval.ipynb`        | TF-IDF/char/math retrieval                       | ⏳ Not started            |
| `06_R2_dense_retrieval.ipynb`         | Dense semantic retrieval                         | ⏳ Not started            |
| `07_R3_candidate_union.ipynb`         | Sparse + dense union                             | ⏳ Not started            |
| `08_cross_encoder_reranking.ipynb`    | Cross-encoder evidence reranking                 | ⏳ Not started            |

---

# 21. Phase Completion Status

## Phase 0 — Environment

```text
████████████████████ 100%
```

```text
SETUP_READY = True
```

## Phase 1 — Data Foundation

```text
████████████████████ 100%
```

```text
17 / 17 hard gates PASS
PHASE 1 FOUNDATION READY = True
```

## Phase 2 — Retrieval

```text
██░░░░░░░░░░░░░░░░░░ ~10%
```

Current:

```text
R0 canonical discovery/schema audit = DONE
R0 artifact construction            = NOT DONE
R1                                = NOT STARTED
R2                                = NOT STARTED
R3                                = NOT STARTED
Cross-Encoder                     = NOT STARTED
```

---

# 22. Current Bottom Line

এখন পর্যন্ত সবচেয়ে গুরুত্বপূর্ণ achievement হলো **model না, reliable evidence foundation** তৈরি করা।

আমাদের কাছে এখন:

```text
35,072 response samples
22,821 sessions
6,139,854 ordered turns
398 canonical objectives
5 frozen session-grouped folds
0 cross-fold session leakage
0 parser final failures
17/17 integrity gates passed
```

এবং canonical source-of-truth এখন frozen:

```text
responses.parquet
turns.parquet
sessions.parquet
objectives.parquet
```

এরপরের **actual next step হলো `04_R0_retrieval_input_builder.ipynb` complete করা**—বিশেষ করে:

```text
retrieval_queries.parquet
session_turn_index.parquet
objective_catalogue.parquet
r0_manifest.json
R0 freeze gate
```

এসব PASS না হওয়া পর্যন্ত **R1 Sparse Retrieval শুরু করা উচিত নয়**। 

---

## Source Files / Notebooks

এই progress summary-এর মূল source:

* `00_environment_and_paths.ipynb`
* `01_data_inventory.ipynb`
* `02_turn_parser.ipynb`
* `03_data_integrity.ipynb`
* `04_R0_retrieval_input_builder.ipynb`
* `dataset_check.ipynb`
* `retrival.md`
* `Trace_the_Ace_Main_Architecture_Full_Step_by_Step.md`
* `Trace_the_Ace_Scratch_Mastery_Roadmap_Bangla.md`
* `full_model_training_part.md`


# Trace the Ace — Phase 1: Data Foundation & True Turn Reconstruction
## Final Step-by-Step Implementation Specification

---

## 0. Purpose of This Document

এই document হলো **Trace the Ace Final Main Architecture**-এর Phase 1 implementation specification।

আমাদের Final Main Architecture শুরু হয়:

```text
RAW ORDERED TRANSCRIPT
        ↓
CANONICAL TURN RECONSTRUCTION
(role + timestamp + true order)
        ↓
LEARNING OBJECTIVE
        ↓
SPARSE + DENSE RETRIEVAL
        ↓
...
```

তাই Phase 1-এর কাজ model train করা নয়, retrieval করা নয়, mastery interpret করা নয়।

Phase 1-এর একমাত্র বড় দায়িত্ব:

> **Official raw data থেকে একটি deterministic, traceable, leakage-safe, inference-compatible এবং trusted canonical evidence layer তৈরি করা।**

Previous analysis-এ student/tutor dialogue true utterance level-এ reconstruct না হয়ে aggregated representation তৈরি হয়েছিল। সেই কারণে retrieval, temporal evidence এবং pre/post-feedback সম্পর্কিত আগের কিছু conclusion trusted turn-level conclusion হিসেবে ব্যবহার করা যাবে না।

এই Phase তাই পুরো advanced architecture-এর foundation।

---

# 1. Final Phase Goal

Phase 1 শেষে আমরা নিচের chain-টি guarantee করতে চাই:

> **Every labelled response → exactly one session → that session's exact ordered utterances → preserved speaker role + timestamp + raw text + provenance → frozen fold assignment পর্যন্ত deterministic এবং traceable।**

Conceptually:

```text
OFFICIAL RAW DATA
        ↓
SOURCE TRUTH
        ↓
RESPONSE FOUNDATION
        ↓
TRUE UTTERANCE RECONSTRUCTION
        ↓
STRUCTURAL + RELATIONAL + SEQUENCE AUDIT
        ↓
LEAKAGE + TRACEABILITY AUDIT
        ↓
CANONICAL DATA FOUNDATION
        ↓
FREEZE
        ↓
PHASE 2 — ADVANCED DIAGNOSTICS
```

---

# 2. Governing Rule

আমাদের project execution rule:

```text
BUILD
  ↓
AUDIT
  ↓
PASS?
 ┌──────┴──────┐
NO            YES
↓              ↓
FIX          FREEZE
CURRENT         ↓
STAGE        NEXT STAGE
```

Therefore:

\[
\boxed{
\text{Stage Complete}
=
\text{Implementation Complete}
+
\text{Validation Passed}
}
\]

কোনো notebook successful run হয়েছে বলেই phase complete হবে না।

---

# 3. Phase 1 Scope Boundary

## Phase 1 করবে

- Authoritative source discovery
- Response/session/objective/label relationship validation
- Frozen fold validation
- Transcript source inventory
- True utterance-level parsing
- Speaker role preservation
- Timestamp preservation এবং parsing
- Deterministic turn ordering
- Stable turn identity
- Raw-to-canonical provenance
- Structural session summaries
- Exact duplicate checks
- Join/cardinality checks
- Data quality flags
- Parser determinism tests
- Training/inference symmetry checks
- Canonical dataset publication
- Phase-level audit report এবং hard gate

## Phase 1 করবে না

```text
❌ Sparse retrieval
❌ Dense retrieval / Sentence-Transformer embeddings
❌ Objective × turn semantic similarity
❌ Cross-Encoder reranking
❌ Objective-specific evidence selection
❌ Student-before / student-after semantic classification
❌ Tutor correction / scaffold classification
❌ Contradiction or uncertainty modelling
❌ Same-session hard-negative generation
❌ ModernBERT
❌ Structured mastery features
❌ Objective prior
❌ OOF model prediction
❌ Calibration
❌ Near-duplicate semantic clustering
```

এই boundary অত্যন্ত গুরুত্বপূর্ণ।

Phase 1 chronology এবং evidence structure **preserve** করবে; evidence meaning **interpret** করবে না।

---

# 4. Final Notebook Structure

```text
01_data_foundation/
│
├── 01_data_inventory.ipynb
│      Question:
│      What exactly is our authoritative data?
│
├── 02_turn_parser.ipynb
│      Question:
│      What exactly happened in every conversation?
│
└── 03_data_integrity.ipynb
       Question:
       Can we trust and freeze this reconstructed foundation?
```

তিনটি notebook-এর responsibility overlap করবে না।

---

# 5. Global Engineering Contracts

Phase 1 implementation শুরু করার আগে নিচের rules freeze থাকবে।

## Contract A — Raw Data Is Immutable

Original values overwrite করা যাবে না।

```text
role_raw       → preserved
role           → derived

timestamp_raw  → preserved
timestamp      → parsed/derived

content_raw    → preserved
text_norm      → safely normalized
```

---

## Contract B — Candidate ≠ Canonical

```text
RAW
 ↓
PARSER OUTPUT
 ↓
CANDIDATE TABLES
 ↓
INTEGRITY AUDIT
 ↓
CANONICAL TABLES
```

Notebook 2-এর output canonical নয়।

Canonical publish করার authority শুধু Notebook 3-এর।

---

## Contract C — No Silent Repair

যদি timestamp invalid হয়:

```text
timestamp_status = UNPARSEABLE
ordering_method  = UTTERANCE_ID_FALLBACK
ordering_issue   = True
```

কিন্তু original timestamp silently replace করা যাবে না।

---

## Contract D — Every Transformation Must Be Traceable

একটি canonical turn থেকে original raw row recover করা সম্ভব হতে হবে:

```text
turn_uid
   ↓
source_file_relative
source_row_index
   ↓
original transcript row
```

---

## Contract E — Every Join Has a Cardinality Contract

Normal `merge()` চালিয়ে result accept করা যাবে না।

প্রতিটি join-এ record করতে হবে:

```text
left_rows
right_rows
expected_cardinality
actual_cardinality
result_rows
unmatched_left
unmatched_right
duplicate_expansion
status
```

---

## Contract F — Frozen Folds Are Immutable

Current frozen fold manifest নতুন করে generate করা হবে না।

Phase 1 শুধু validate করবে।

Future retrieval, transformer, prior, fusion, calibration—সব একই split manifest respect করবে।

---

## Contract G — Parser Is Label-Blind

Turn parser ব্যবহার করতে পারবে না:

```text
target
OOF prediction
objective prior
baseline prediction
validation metric
```

Parser purely structural থাকবে।

---

## Contract H — Determinism Is Mandatory

Same input + same parser version:

```text
Run A == Run B
```

for:

```text
row count
turn order
turn_uid
normalized text
quality flags
hashes
```

---

## Contract I — Machine-Independent Identity

`turn_uid` absolute Windows path বা machine-specific path-এর উপর depend করবে না।

---

## Contract J — Stage Output Must Be Reusable

Phase 2/3-এ আবার raw transcript reparsing করার প্রয়োজন হওয়া উচিত নয়।

Canonical `turns.parquet`-এ downstream-এর প্রয়োজনীয় structural information already থাকতে হবে।

---

# 6. Output Strategy — Minimal but Robust

অনেক ছোট CSV/Parquet তৈরি না করে তিন ধরনের output থাকবে।

## A. Core machine-readable tables → Parquet

```text
responses.parquet
turns.parquet
sessions.parquet
objectives.parquet
```

## B. Human-readable audit → One Excel workbook

```text
phase1_data_foundation_audit.xlsx
```

## C. Machine contracts / manifests → JSON

```text
data_contract.json
phase1_manifest.json
phase1_gate.json
```

Large exception rows Excel-এর জন্য বেশি হলে optional:

```text
audit_exceptions.parquet
```

---

# FILE 01 — `01_data_inventory.ipynb`

# 7. Notebook 1 Goal

Notebook 1 answer করবে:

> **আমাদের actual source data কী, কোন source কোন information-এর authority, schema/key relationship কী, transcript coverage কী, এবং parser কোন exact data contract follow করবে?**

Notebook 1 transcript reconstruct করবে না।

---

## Section 1.0 — Foundation Bootstrap & Run Identity

### Objective

Phase run-এর context এবং source registry load করা।

### Inputs

```text
path_registry.json
setup_summary.json
source_fingerprints.json
frozen_fold_manifest.parquet
```

### Record

```text
phase_name
contract_version
run_id
run_timestamp
git_commit
git_dirty
```

### Example

```text
phase              : data_foundation
contract_version   : 1.0
run_id             : DF_20260808_001
run_status         : STARTED
```

### Audit

- Required configuration files exist?
- Registered paths resolve?
- Frozen fold manifest readable?
- Source fingerprints readable?

### Exit condition

```text
FOUNDATION_BOOTSTRAP_READY = TRUE
```

---

## Section 1.1 — Authoritative Source Mapping

### Objective

Official raw source এবং old derived/reference files আলাদা করা।

### Expected authority map

| Source | Authority |
|---|---|
| Train features | Response/session/objective metadata |
| Train labels | Target |
| Raw transcripts | Utterance text, role, timestamp |
| Frozen fold manifest | Validation fold assignment |
| Submission format | Future inference schema reference |
| Old master dataset | Reference only |
| Baseline OOF | Diagnostic reference only |
| Previous parser outputs | Reference only |

### Rule

```text
Official raw source
        >
Old derived artefact
```

### Why

New Scratch Mastery foundation previous representation mistake inherit করবে না।

### Output

Source registry table in memory এবং later Excel audit sheet।

---

## Section 1.2 — Source Fingerprint & Schema Drift Check

### Objective

Accidental file replacement, schema mutation বা wrong source detect করা।

### For each source record

```text
relative_path
file_size
modified_time
content_hash / registered fingerprint
column_signature
row_count
```

Transcript directory-এর জন্য:

- sorted file manifest
- directory-level deterministic fingerprint

### Audit

```text
registered source == current source?
schema changed unexpectedly?
row count changed unexpectedly?
```

### Important

এই check reproducibility-এর জন্য; arbitrary old metadata mismatch দেখলেই blindly fail করা হবে না।

Current authoritative source truth first priority।

---

## Section 1.3 — Schema Discovery & Key Resolution

### Objective

Actual column names এবং key relationship data থেকেই establish করা।

### Profile

```text
column_name
dtype
null_count
non_null_count
unique_count
duplicate_count
candidate_key
```

### Resolve

```text
response_key
session_key
objective_field
target_field
fold_field
```

### Example

| Entity | Field | Expected property |
|---|---|---|
| Response | `response_id` | unique |
| Session | `session_id` | repeated allowed |
| Objective | learning-objective field | non-empty |
| Target | target field | binary |

### Hard checks

```text
features response IDs == label response IDs
response_id unique
session_id non-null
objective non-empty
target ∈ {0,1}
```

### Exit condition

```text
SCHEMA_KEYS_VALID = TRUE
```

---

## Section 1.4 — Build `responses_base.parquet`

### Objective

Official response-level prediction population establish করা।

### Unit

> **1 row = 1 session × learning objective response**

### Minimum schema

```text
response_id
session_id
objective_raw
target
fold
```

### Example

| response_id | session_id | objective_raw | target | fold |
|---|---|---|---:|---:|
| R001 | S101 | Compare fractions with different denominators | 1 | 2 |
| R002 | S101 | Add fractions with different denominators | 0 | 2 |

### Deliberately absent

```text
objective_prior
OOF_probability
semantic_score
retrieval_score
TF-IDF_features
```

### Audit

- Unique `response_id`
- One label per response
- One fold per response
- Valid session
- Non-empty objective
- No row multiplication during feature-label join

---

## Section 1.5 — Population Census

### Objective

Current authoritative population document করা।

### Compute

```text
n_responses
n_sessions
n_objectives_raw
n_objectives_safe_norm
n_positive
n_negative
positive_rate
responses_per_session distribution
objectives_per_session distribution
```

### Known baseline reference

```text
responses ≈ 35,072
sessions  ≈ 22,821
positive rate ≈ 70.25%
```

Reference values validation aid; current authoritative data is source of truth।

---

## Section 1.6 — Objective Population Reconciliation

### Objective

Current objective population deterministicভাবে establish করা এবং previous `398 vs 396` discrepancy explain করার চেষ্টা করা।

### Compare

```text
raw exact objective
safe-normalized objective
case-normalized diagnostic key
fold-covered objective
baseline-OOF objective
```

### Important Improvement

Historical `398 vs 396` difference **blind hard blocker নয়**।

Hard requirement হলো:

> **Current authoritative objective population must be deterministic, reproducible and documented.**

যদি old baseline artefact থেকে difference fully explain করা যায়, explanation save করা হবে।

যদি old artefact incomplete/unavailable হয় কিন্তু current official data internally consistent হয়:

```text
CURRENT_OBJECTIVE_POPULATION = PASS
HISTORICAL_RECONCILIATION   = WARNING / DOCUMENTED
```

Phase unnecessarily stop করা হবে না।

### Example audit

| objective_raw | safe_norm | current_rows | baseline_present | status |
|---|---|---:|---|---|
| Objective X | Objective X | 71 | Yes | MATCH |
| Objective x | Objective x | 12 | No | HISTORICAL_DIFFERENCE |

---

## Section 1.7 — Transcript File Inventory

### Objective

Transcript directory-এর actual structure establish করা।

### Per file record

```text
relative_file
file_size
row_count
columns
session_ids_inside
read_status
schema_status
```

### Required source fields

```text
session_id
utterance_id
role
content
timestamp
```

### Checks

```text
corrupt file?
empty file?
required field missing?
unexpected schema?
duplicate file?
filename/session disagreement?
```

### Important Improvement

এক session multiple files-এ থাকলেই automatically blocker নয়।

First classify:

```text
SINGLE_SOURCE
MULTI_SOURCE_VALID
MULTI_SOURCE_AMBIGUOUS
```

Only ambiguous duplication becomes blocker।

---

## Section 1.8 — Transcript Session Coverage

### Objective

Every labelled session-এর transcript availability establish করা।

### Compare

```text
response sessions
        VS
transcript sessions
```

### Status

```text
MATCHED
MISSING_TRANSCRIPT
ORPHAN_TRANSCRIPT
MULTI_SOURCE_VALID
MULTI_SOURCE_AMBIGUOUS
```

### Example

| session_id | response_exists | transcript_exists | status |
|---|---:|---:|---|
| S101 | 1 | 1 | MATCHED |
| S102 | 1 | 0 | BLOCKER |
| S999 | 0 | 1 | ORPHAN |

### Hard requirement

Every labelled response session must resolve to usable transcript evidence।

---

## Section 1.9 — Frozen Fold Contract

### Objective

Existing grouped validation manifest validate করা।

### Check

```text
every response → exactly one fold
every session  → exactly one fold
zero session cross-fold overlap
no duplicate response assignment
no missing response assignment
fold IDs valid
```

### Summary

| Check | Requirement |
|---|---|
| Response coverage | 100% |
| Duplicate fold assignment | 0 |
| Session cross-fold overlap | 0 |

### Important

No fold recreation।

---

## Section 1.10 — Create `data_contract.json`

### Objective

Notebook 2 parser-এর জন্য explicit machine-readable contract তৈরি করা।

### Why this was improved

`data_contract.json` Notebook 3-এ প্রথম তৈরি করলে parser contract formally unavailable থাকে।

তাই **Notebook 1-এই contract তৈরি হবে**।

### Example structure

```json
{
  "contract_version": "1.0",
  "response_key": "response_id",
  "session_key": "session_id",
  "objective_field": "objective_raw",
  "target_field": "target",
  "transcript_required_fields": [
    "session_id",
    "utterance_id",
    "role",
    "content",
    "timestamp"
  ],
  "ordering_policy_version": "1.0",
  "normalization_policy_version": "1.0",
  "frozen_fold_manifest_hash": "..."
}
```

### Rule

Notebook 2 parser এই contract read করবে; duplicate hardcoded assumptions রাখবে না।

---

## Section 1.11 — Inventory Audit Questions

Notebook 1 stage complete হওয়ার আগে চারটি প্রশ্ন:

### Correctness

Authoritative sources ঠিকভাবে identified?

### Coverage

Every response/session/source accounted for?

### Failure Analysis

Mismatch কোথায় এবং কী type-এর?

### Downstream Readiness

Parser safely start করতে পারবে?

---

## Section 1.12 — Inventory Gate

### Final variable

```text
INVENTORY_READY = TRUE / FALSE
```

### BLOCKER conditions

```text
feature-label population mismatch
invalid response key
invalid target
missing labelled-session transcript
ambiguous transcript source
invalid fold assignment
session crossing folds
required schema corruption
current objective population internally inconsistent
```

### Warning examples

```text
historical objective-count discrepancy not fully explainable
orphan unused transcript
non-critical metadata difference
```

### Outputs

```text
01_inventory/
├── responses_base.parquet
└── inventory_manifest.json

01_data_foundation/
└── data_contract.json
```

---

# FILE 02 — `02_turn_parser.ipynb`

# 8. Notebook 2 Goal

Notebook 2 answer করবে:

> **প্রতিটি session-এ আসলে কে কী বলেছে, কখন বলেছে এবং কোন deterministic order-এ utterances ঘটেছে?**

এটাই Phase 1-এর technical heart।

---

## Section 2.0 — Parser Entry Contract

### Inputs

```text
data_contract.json
inventory_manifest.json
responses_base.parquet
registered transcript sources
```

### Require

```text
INVENTORY_READY == TRUE
```

### Additional check

Source fingerprint Notebook 1-এর পর change হয়েছে কিনা।

Mismatch হলে stop।

---

## Section 2.1 — Raw Utterance Ingestion

### Objective

Raw transcript row intact রেখে ingest করা।

### Preserve

```text
session_id_raw
utterance_id_raw
role_raw
content_raw
timestamp_raw

source_file_relative
source_row_index
```

### Rule

```text
RAW FIELD ≠ DERIVED FIELD
```

---

## Section 2.2 — Pre-Parse Structural Audit

### Why before cleaning?

Cleaning-এর পরে raw anomaly hide হয়ে যেতে পারে।

### Detect

```text
missing session_id
missing utterance_id
missing role
missing content
missing timestamp
duplicate utterance_id within session
exact duplicated raw row
```

### Output

Quality flags attached to raw working table।

No row deletion unless source row is proven unusable and the decision is explicitly audited।

---

## Section 2.3 — Canonical Naming Standard

Consistency-এর জন্য Phase 1 naming freeze করা হবে।

### Preferred names

```text
content_raw       # exact source text
text_norm         # safe normalized text

timestamp_raw
timestamp

utterance_id_raw
utterance_id

role_raw
role
```

একই concept-এর জন্য `text_raw`, `content_raw`, `content_clean` ইত্যাদি mixed naming ব্যবহার করা হবে না।

---

## Section 2.4 — Safe Text Normalization

### Preserve

```text
content_raw
```

### Create

```text
text_norm
```

### Allowed

```text
Unicode normalization
line-ending normalization
leading/trailing whitespace trim
repeated whitespace collapse
```

### Not allowed

```text
❌ stopword removal
❌ stemming
❌ punctuation stripping
❌ number rewriting
❌ spell correction
❌ LLM correction
❌ [UNCLEAR] deletion
❌ semantic rewriting
```

Mathematical notation must survive।

Example:

```text
1/3 < 1/2
```

must retain meaning exactly।

---

## Section 2.5 — Role Canonicalization

### Process

1. First inspect actual unique role values.
2. Define explicit versioned role map.
3. Normalize formatting variants only.

Example:

```text
"STUDENT"   → student
" Student " → student
"Tutor"     → tutor
```

Unknown role:

```text
role = unknown
role_issue_flag = True
```

### Rule

Lexical text দেখে speaker identity guess করে automatic rewrite করা যাবে না।

---

## Section 2.6 — Timestamp Parsing

### Preserve

```text
timestamp_raw
```

### Create

```text
timestamp
timestamp_status
```

Possible status:

```text
VALID
MISSING
UNPARSEABLE
```

### Derived values

Only when valid:

```text
time_since_previous_turn
elapsed_from_session_start
```

Invalid timestamp হলে derived temporal values `null` থাকতে পারে।

No fake timestamp generation।

---

## Section 2.7 — Utterance-ID Parsing

### Preserve

```text
utterance_id_raw
```

### Create

```text
utterance_id
utterance_id_status
```

Possible status:

```text
VALID
MISSING
UNPARSEABLE
DUPLICATED_WITHIN_SESSION
```

Numeric-like IDs হলে deterministic numeric ordering preferred।

Otherwise deterministic lexical/natural ordering policy versioned থাকবে।

---

## Section 2.8 — Deterministic Turn Ordering Engine

### Primary rule

```text
timestamp
    ↓
utterance_id
    ↓
source_file_relative
    ↓
source_row_index
```

### Fallback A — Timestamp unavailable

```text
utterance_id
    ↓
source_file_relative
    ↓
source_row_index
```

### Fallback B — Timestamp + utterance ID unusable

```text
source_file_relative
    ↓
source_row_index
```

### Store

```text
ordering_method
ordering_confidence
ordering_issue_flag
```

Example:

```text
ordering_method     = TIMESTAMP_THEN_ID
ordering_confidence = HIGH
ordering_issue_flag = False
```

or:

```text
ordering_method     = SOURCE_ORDER_FALLBACK
ordering_confidence = LOW
ordering_issue_flag = True
```

---

## Section 2.9 — Ordering Conflict Audit

### Compare

```text
source order
timestamp order
utterance-id order
selected canonical order
```

### Flags

```text
TIMESTAMP_ID_CONFLICT
SOURCE_TIMESTAMP_CONFLICT
AMBIGUOUS_ORDER
FALLBACK_USED
```

### Why

Final `turn_index` deterministic হলেও uncertainty hide করা যাবে না।

---

## Section 2.10 — Stable Turn Identity

### Create

```text
turn_uid
```

### Properties

- deterministic
- unique
- machine-independent
- path-independent
- reproducible under same source data + parser version

### Suggested logic

If utterance ID unique within session:

```text
hash(session_id + utterance_id_raw)
```

If duplicate/ambiguous:

```text
hash(
    session_id
    + utterance_id_raw
    + timestamp_raw
    + content_raw
    + duplicate_occurrence_index
)
```

### Also store

```text
raw_row_hash
content_hash
turn_uid_version
```

### Separation

```text
turn_uid      → identity
content_hash  → evidence verification
source fields → provenance
```

---

## Section 2.11 — Structural Turn Metadata

### Create

```text
turn_index
role_turn_index
relative_turn_position

previous_role
next_role
speaker_switch

time_since_previous_turn
elapsed_from_session_start

is_first_turn
is_last_turn
```

### Important boundary

Phase 1 will NOT infer:

```text
tutor_correction
tutor_scaffold
student_mastery
contradiction
feedback_effect
student_after_feedback
```

Those are later objective-conditioned semantic concepts।

---

## Section 2.12 — Build `turns_candidate.parquet`

### Unit

> **1 row = 1 real utterance**

### Core example

| session_id | turn_uid | turn_index | role | timestamp | content_raw |
|---|---|---:|---|---|---|
| S101 | T001 | 0 | tutor | 10:01 | Which is larger, 1/3 or 1/4? |
| S101 | T002 | 1 | student | 10:02 | I think 1/4. |
| S101 | T003 | 2 | tutor | 10:03 | Think about the size of each piece. |

### Core guarantee

```text
Student/tutor aggregation = PROHIBITED
```

---

## Section 2.13 — Build `sessions_candidate.parquet`

### Unit

> **1 row = 1 tutoring session**

### Fields

```text
session_id
n_turns
n_student_turns
n_tutor_turns
n_other_turns
n_unknown_roles

first_valid_timestamp
last_valid_timestamp
duration_seconds
duration_status

timestamp_issue_count
ordering_issue_count
empty_content_count
unknown_role_count

raw_transcript_hash
normalized_transcript_hash
```

### Important

Transcript hash must be **order-sensitive**।

```text
hash(turn_hash_0 + turn_hash_1 + ... + turn_hash_n)
```

Same turns in different order → different transcript hash।

---

## Section 2.14 — Synthetic Parser Unit Tests

এটা final plan-এর গুরুত্বপূর্ণ improvement।

Real dataset শুধু test করলে rare edge-case missed হতে পারে।

Parser-এর জন্য small synthetic sessions তৈরি করা হবে।

### Test cases

```text
T01 normal timestamps + unique IDs
T02 same timestamp, different utterance IDs
T03 missing timestamp
T04 malformed timestamp
T05 duplicate utterance ID
T06 duplicate text with different IDs
T07 unknown role
T08 multiple source files for one session
T09 all timestamps missing
T10 source row fallback
```

### Example

Input:

```text
10:01  U1  tutor    Question
10:01  U2  student  Answer
```

Expected order:

```text
U1 → U2
```

### Requirement

Every synthetic test has explicit expected output।

This prevents parser behaviour from being accidentally changed later।

---

## Section 2.15 — Parser Determinism Test

Same real-data subset twice parse করা হবে।

Compare:

```text
row_count
turn_uid
turn_index
role
timestamp
text_norm
ordering flags
session hashes
```

Requirement:

```text
100% identical
```

---

## Section 2.16 — Stratified Human Reconstruction Audit

Random sample alone যথেষ্ট নয়।

Include sessions with:

```text
short session
long session
timestamp tie
missing timestamp
duplicate utterance ID
unknown role
[UNCLEAR]-heavy text
many speaker switches
duplicate content
fallback ordering
multi-source session
```

### Display

| turn_index | timestamp | role | content_raw |
|---:|---|---|---|
| 0 | 10:01 | Tutor | Which is larger...? |
| 1 | 10:02 | Student | I think 1/4. |
| 2 | 10:03 | Tutor | Think about... |

### Human question

> Original conversation chronology intact আছে কি?

---

## Section 2.17 — Parser Audit Questions

### Correctness

One raw utterance truly one candidate turn হয়েছে?

### Coverage

Any source rows lost?

### Failure Analysis

Which sessions needed fallback এবং কেন?

### Downstream Readiness

Phase 2/3 কি এই turns পুনরায় parse না করেই use করতে পারবে?

---

## Section 2.18 — Parser Gate

Final:

```text
PARSER_READY_FOR_INTEGRITY = TRUE / FALSE
```

### BLOCKER examples

```text
non-deterministic output
row loss without documented reason
duplicate candidate turn keys
unrecoverable source provenance
systematic ordering corruption
```

### WARNING examples

```text
rare fallback ordering
unknown role
missing timestamps with deterministic fallback
```

### Outputs

```text
02_turn_parser/
├── turns_candidate.parquet
├── sessions_candidate.parquet
└── parser_manifest.json
```

---

# FILE 03 — `03_data_integrity.ipynb`

# 9. Notebook 3 Goal

Notebook 3 answer করবে:

> **Notebook 1 এবং Notebook 2-এর reconstructed data scientifically ও data-engineering-wise trustworthy কি না, এবং এটাকে final canonical foundation হিসেবে freeze করা safe কি না?**

এই notebook certification layer।

---

## Section 3.0 — Integrity Bootstrap & Fingerprint Verification

### Inputs

```text
data_contract.json
responses_base.parquet
turns_candidate.parquet
sessions_candidate.parquet
inventory_manifest.json
parser_manifest.json
frozen_fold_manifest.parquet
```

### Check

```text
source fingerprints unchanged?
candidate hashes match parser manifest?
contract version match?
parser version match?
```

Mismatch → stop।

---

## Section 3.1 — Response Key Integrity

### Check

```text
response_id unique
session_id valid
objective non-empty
target valid
fold valid
```

Any violation → BLOCKER।

---

## Section 3.2 — Turn Key Integrity

### Check

```text
turn_uid unique
(session_id, turn_index) unique
raw source row represented as expected
```

### Additional check

Same `turn_uid` different content → BLOCKER।

---

## Section 3.3 — Session Key Integrity

### Check

```text
session_id unique in sessions_candidate
n_turns matches actual turns
role counts match actual turns
```

---

## Section 3.4 — Relational Integrity

### Required relationship

```text
RESPONSES
    M : 1
SESSIONS

SESSIONS
    1 : M
TURNS
```

### For each join log

```text
left_rows
right_rows
expected_cardinality
actual_cardinality
result_rows
unmatched_left
unmatched_right
duplicate_expansion
```

### Example

| Join | Expected | Observed | Result |
|---|---|---|---|
| Response → Session | M:1 | M:1 | PASS |
| Session → Turn | 1:M | 1:M | PASS |

No silent many-to-many explosion।

---

## Section 3.5 — Coverage Integrity

### Required chain

```text
every labelled response
        ↓
exactly one session
        ↓
at least one usable turn
```

Target:

```text
100% labelled-session coverage
```

---

## Section 3.6 — Sequential Integrity

Per session:

```text
min(turn_index) = 0
max(turn_index) = n_turns - 1
count(unique turn_index) = n_turns
```

Also:

```text
no gaps
first-turn flag correct
last-turn flag correct
relative_turn_position valid
```

---

## Section 3.7 — Timestamp & Ordering Integrity

### Metrics

```text
valid timestamp rate
missing timestamp rate
unparseable timestamp rate
timestamp ties
timestamp/ID conflicts
fallback-order sessions
low-confidence-order sessions
zero-duration sessions
extreme time gaps
```

### Key metric

```text
percentage of sessions requiring fallback ordering
```

### Severity principle

Arbitrary hard threshold আগে থেকে invent করা হবে না।

Distribution inspect করা হবে।

If issue is rare and deterministic fallback works:

```text
WARNING
```

If issue is systemic and chronology cannot be trusted:

```text
BLOCKER
```

---

## Section 3.8 — Role Integrity

### Check

```text
no student turn
no tutor turn
unknown role
single-role session
extreme same-speaker run
```

### Rule

Flag first, never silently correct।

---

## Section 3.9 — Text Integrity

### Check

```text
empty content
whitespace-only content
[UNCLEAR]
extreme utterance length
exact consecutive duplicate
repeated ASR fragment
```

### Rule

```text
FLAG ≠ DELETE
```

Text quality issue future retrieval/model analysis-এর input হতে পারে।

---

## Section 3.10 — Exact Transcript Duplicate Audit

### Hashes

```text
raw_transcript_hash
normalized_transcript_hash
```

Detect:

```text
different session IDs
same exact raw transcript

different session IDs
same safe-normalized transcript
```

Assign deterministic duplicate-group identifiers।

---

## Section 3.11 — Exact Objective Duplicate Audit

Check:

```text
raw exact objective equality
safe-normalized exact objective equality
```

No semantic embeddings here।

Near-duplicate objectives belong to Phase 2।

---

## Section 3.12 — Response Collision & Label Conflict Audit

### Check A

```text
same session + same objective repeated?
```

### Check B

```text
same exact transcript
+
same normalized objective
+
different target
```

Flag:

```text
LABEL_CONFLICT_CANDIDATE
```

### Rule

Never automatically relabel।

Target future quiz outcome হওয়ায় apparently similar evidence-এর different labels legitimate হতে পারে।

---

## Section 3.13 — Frozen Fold Leakage Audit

### Hard leakage check

```text
same session appears in multiple folds
```

Required:

```text
0
```

### Separate memorization-risk check

```text
different session IDs
same exact transcript
different folds
```

This is NOT automatically direct session leakage।

Flag:

```text
EXACT_DUPLICATE_CROSS_FOLD_RISK
```

Phase 2 duplicate-cluster stress validation handle করবে।

---

## Section 3.14 — Raw-to-Canonical Traceability Audit

Sample candidate/final turns across multiple strata।

Trace:

```text
turn_uid
    ↓
source_file_relative
source_row_index
    ↓
raw source row
```

Recover exactly:

```text
session_id
utterance_id
role
content
timestamp
```

Requirement:

```text
100% exact recovery for tested rows
```

For full automated hash/key traceability, no orphan canonical turn allowed।

---

## Section 3.15 — Serialization Round-Trip Audit

### Process

```text
save candidate/final parquet
        ↓
reload
        ↓
compare
```

### Check

```text
row count
column names
dtypes
key uniqueness
content hashes
ordering
```

Disk artefact must equal verified in-memory dataset।

---

## Section 3.16 — Training / Inference Symmetry Audit

### Objective

Final parser একই raw schema দিয়ে unseen test session independently process করতে পারে কিনা verify করা।

### Parser must NOT require

```text
target
fold-specific label statistic
OOF prediction
objective prior
other test sessions
test-set aggregates
```

### Test

Selected session-এর parser input থেকে labels/folds completely remove করে parse করা।

Expected structural output same।

---

## Section 3.17 — Build Canonical `objectives.parquet`

### Unit

> **1 row = 1 canonical objective text identity**

### Example

| objective_uid | objective_raw | objective_safe_norm | response_count | session_count |
|---|---|---|---:|---:|
| O001 | Compare fractions... | Compare fractions... | 128 | 117 |

### Deliberately absent

```text
❌ global positive rate
❌ objective label mean
❌ objective prior
```

Those target-dependent statistics later fold-safeভাবে build হবে।

---

## Section 3.18 — Quality Flags Integration

Separate `session_quality.parquet` mandatory করা হবে না।

Quality fields appropriate canonical table-এই থাকবে।

### Turn-level examples

```text
role_issue_flag
timestamp_issue_flag
ordering_issue_flag
empty_content_flag
```

### Session-level examples

```text
timestamp_issue_count
ordering_issue_count
unknown_role_count
fallback_order_used
exact_duplicate_group
quality_warning_count
```

এতে file count কমে এবং data relationship simple থাকে।

---

## Section 3.19 — Canonical Publication

### Only if all blocking integrity checks pass

```text
candidate
    ↓
write temporary canonical files
    ↓
reload
    ↓
verify fingerprints
    ↓
atomic promote
    ↓
CANONICAL FOUNDATION
```

### Final canonical tables

```text
canonical/
├── responses.parquet
├── turns.parquet
├── sessions.parquet
└── objectives.parquet
```

---

## Section 3.20 — Phase Audit Workbook

One workbook:

```text
phase1_data_foundation_audit.xlsx
```

### Recommended sheets

```text
00_PHASE_SUMMARY
01_SOURCE_REGISTRY
02_SCHEMA_KEYS
03_POPULATION
04_OBJECTIVE_RECONCILIATION
05_TRANSCRIPT_COVERAGE
06_FOLD_INTEGRITY
07_PARSER_SUMMARY
08_ORDERING_TIMESTAMP
09_ROLE_TEXT_QUALITY
10_EXACT_DUPLICATES
11_LABEL_COLLISIONS
12_JOIN_INTEGRITY
13_TRACEABILITY
14_SERIALIZATION
15_INFERENCE_SYMMETRY
16_FINAL_GATE
```

### `00_PHASE_SUMMARY` example

| Metric | Result |
|---|---:|
| Responses | 35,072 or actual authoritative result |
| Sessions | 22,821 or actual authoritative result |
| Turns | actual |
| Objectives | reconciled current result |
| Labelled transcript coverage | target 100% |
| Session fold overlap | target 0 |
| Parser deterministic | target 100% |
| Blockers | target 0 |
| Phase status | PASS / FAIL |

### `16_FINAL_GATE` example

| Gate | Requirement | Observed | Status |
|---|---|---|---|
| Source identity | valid | ... | PASS/FAIL |
| Response key | unique | ... | PASS/FAIL |
| Transcript coverage | complete | ... | PASS/FAIL |
| Session fold overlap | 0 | ... | PASS/FAIL |
| Parser deterministic | 100% | ... | PASS/FAIL |
| Traceability | valid | ... | PASS/FAIL |

### Large exceptions

If exception rows are too large for useful Excel inspection:

```text
audit_exceptions.parquet
```

Only then create it।

---

## Section 3.21 — Final `phase1_manifest.json`

### Example

```json
{
  "phase": "data_foundation",
  "contract_version": "1.0",
  "parser_version": "1.0",
  "response_count": 35072,
  "session_count": 22821,
  "turn_count": "...actual...",
  "objective_count": "...current authoritative...",
  "inventory_passed": true,
  "parser_passed": true,
  "integrity_passed": true,
  "blocking_failures": 0,
  "frozen_fold_hash": "...",
  "canonical_responses_hash": "...",
  "canonical_turns_hash": "...",
  "canonical_sessions_hash": "...",
  "canonical_objectives_hash": "..."
}
```

---

## Section 3.22 — Final `phase1_gate.json`

Machine-readable gate summary।

Example:

```json
{
  "PHASE_1_FOUNDATION_READY": true,
  "blockers": 0,
  "errors": 0,
  "warnings": 14,
  "gates": {
    "source_identity": true,
    "response_alignment": true,
    "transcript_coverage": true,
    "session_fold_isolation": true,
    "parser_determinism": true,
    "turn_key_integrity": true,
    "join_integrity": true,
    "traceability": true,
    "serialization": true,
    "inference_symmetry": true
  }
}
```

---

## Section 3.23 — Integrity Audit Questions

### Correctness

Candidate tables represent raw data correctly?

### Coverage

All labelled responses have usable session evidence?

### Failure Analysis

Which anomalies exist, how severe, and where?

### Downstream Readiness

Phase 2/3 can safely use canonical tables without reinterpretation?

---

## Section 3.24 — FINAL HARD GATE

Final:

```text
PHASE_1_FOUNDATION_READY = TRUE / FALSE
```

### Non-negotiable gates

```text
G01  Current source/schema identity valid

G02  Feature-label response population aligned

G03  response_id unique

G04  Target valid

G05  Current authoritative objective population deterministic

G06  Labelled-session transcript coverage valid

G07  Every response assigned to exactly one frozen fold

G08  Zero session cross-fold overlap

G09  Parser deterministic

G10  Turn identity unique

G11  Within-session turn sequence contiguous

G12  Response → Session → Turn relationships valid

G13  No silent many-to-many join expansion

G14  Raw → canonical provenance valid

G15  Serialization round-trip valid

G16  Parser independent of target/test aggregates

G17  Canonical files published only after audit PASS
```

### Historical objective mismatch handling

```text
398 vs 396 fully explained
    → PASS documentation

not fully explainable but current official population internally valid
    → WARNING, not automatic phase failure
```

---

# 10. Issue Severity System

সব anomaly একই severity পাবে না।

## BLOCKER

Phase stop।

Examples:

```text
missing labelled-session transcript
same session crossing folds
duplicate response ID
broken response-session relationship
broken session-turn relationship
non-deterministic parser
duplicate canonical turn key
untraceable canonical row
systemic unusable ordering
```

---

## ERROR

Normally fix/review required before freeze।

Examples:

```text
unexpected role schema
major timestamp parsing failure
ambiguous multi-source session
source/session mismatch
```

---

## WARNING

Data preserve; downstream aware।

Examples:

```text
timestamp missing but deterministic fallback works
rare unknown role
exact cross-session duplicate
zero duration with otherwise trustworthy order
historical objective-count discrepancy
```

---

## INFO

Document only।

Examples:

```text
[UNCLEAR]
very long utterance
orphan unused transcript
```

### Escalation principle

A warning can become BLOCKER if frequency/pattern suggests systemic corruption।

---

# 11. Final Output Structure

```text
scratch_mastery_outputs/
└── 01_data_foundation/
    │
    ├── data_contract.json
    │
    ├── 01_inventory/
    │   ├── responses_base.parquet
    │   └── inventory_manifest.json
    │
    ├── 02_turn_parser/
    │   ├── turns_candidate.parquet
    │   ├── sessions_candidate.parquet
    │   └── parser_manifest.json
    │
    └── 03_integrity/
        │
        ├── canonical/
        │   ├── responses.parquet
        │   ├── turns.parquet
        │   ├── sessions.parquet
        │   └── objectives.parquet
        │
        ├── phase1_data_foundation_audit.xlsx
        ├── phase1_manifest.json
        ├── phase1_gate.json
        │
        └── audit_exceptions.parquet   # conditional only
```

Mandatory final artefacts:

```text
4 canonical Parquet tables
1 audit Excel workbook
1 data contract JSON
1 phase manifest JSON
1 phase gate JSON
```

Candidate files remain because they provide audit lineage between parsing and canonical publication।

---

# 12. Canonical Table Contracts

## `responses.parquet`

### Unit

```text
1 row = 1 response = 1 session × objective
```

### Core fields

```text
response_id
session_id
objective_raw
target
fold
```

---

## `turns.parquet`

### Unit

```text
1 row = 1 actual utterance
```

### Core fields

```text
session_id
turn_uid
turn_index

utterance_id_raw
utterance_id

role_raw
role

content_raw
text_norm

timestamp_raw
timestamp

relative_turn_position
previous_role
next_role
speaker_switch

time_since_previous_turn
elapsed_from_session_start

ordering_method
ordering_confidence
ordering_issue_flag

source_file_relative
source_row_index

raw_row_hash
content_hash
```

---

## `sessions.parquet`

### Unit

```text
1 row = 1 tutoring session
```

### Core fields

```text
session_id
n_turns
n_student_turns
n_tutor_turns
n_other_turns
n_unknown_roles

first_valid_timestamp
last_valid_timestamp
duration_seconds
duration_status

timestamp_issue_count
ordering_issue_count
unknown_role_count
empty_content_count

fallback_order_used
raw_transcript_hash
normalized_transcript_hash
exact_duplicate_group
quality_warning_count
```

---

## `objectives.parquet`

### Unit

```text
1 row = 1 canonical objective identity
```

### Core fields

```text
objective_uid
objective_raw
objective_safe_norm
response_count
session_count
```

### No target statistics

```text
NO global objective label mean
NO global objective prior
```

---

# 13. Why This Phase Is Advanced

Phase 1-এ ModernBERT বা embedding ব্যবহার না করলেও এটি advanced কারণ foundation হবে:

```text
Deterministic
+
Traceable
+
Versioned
+
Leakage-safe
+
Fold-aware
+
Inference-compatible
+
Auditable
+
Reproducible
+
Failure-aware
```

Powerful model wrong evidence পেলে wrong thing আরও efficiently শিখবে।

তাই first responsibility:

\[
\boxed{
\text{Correct Evidence Unit First}
}
\]

---

# 14. Phase 1 Completion Definition

Phase 1 complete হবে না যখন:

```text
turn parser code finished
```

Phase 1 complete হবে যখন:

```text
Official source
   ↓
Response population verified
   ↓
Transcript coverage verified
   ↓
True turns reconstructed
   ↓
Ordering audited
   ↓
Keys and joins audited
   ↓
Fold isolation verified
   ↓
Duplicates documented
   ↓
Traceability verified
   ↓
Serialization verified
   ↓
Inference symmetry verified
   ↓
Canonical tables atomically published
   ↓
FINAL HARD GATE PASS
```

Then:

```text
PHASE_1_FOUNDATION_READY = TRUE
```

---

# 15. Architecture Position After Phase 1

Before:

```text
RAW TRANSCRIPT
      ↓
?
```

After:

```text
RAW TRANSCRIPT
       ↓
TRUSTED CANONICAL TURNS ✅
       ↓
role preserved ✅
timestamp preserved ✅
true order established ✅
raw text preserved ✅
provenance preserved ✅
response/session relation verified ✅
frozen fold relation verified ✅
quality flags preserved ✅
```

Only then:

```text
PHASE 2
Advanced Turn / Session / Objective / Pair Diagnostics

        ↓

PHASE 3
Objective-Conditioned Retrieval

        ↓

Sparse + Dense Retrieval
        ↓
Cross-Encoder
        ↓
Role + Time Evidence Pack
        ↓
ModernBERT
        ↓
...
```

---

# 16. Final Decision

এই Phase 1 design-এর central principle:

> **Data Foundation is not “data cleaning”. It is the certified evidence layer of the Final Main Architecture.**

আর Phase 1-এর সবচেয়ে গুরুত্বপূর্ণ success condition:

> **No semantic/model intelligence enters early, no raw evidence is silently destroyed, no join silently changes population, no fold leakage is introduced, and every canonical turn can be traced back to its original source.**

Once all gates pass:

\[
\boxed{
\text{PHASE 1 — DATA FOUNDATION = FROZEN}
}
\]

এরপরই আমরা Phase 2-তে যাব।

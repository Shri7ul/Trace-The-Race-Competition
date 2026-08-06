# Trace the Ace — Competition Rules & Compliance Report

**Competition:** Trace the Ace (Tutoring Outcomes Prediction Challenge)
**Host / Platform:** DrivenData, on the K‑12 AI Infrastructure Program platform
**Sponsor:** National Tutoring Observatory (NTO), managed by Digital Promise
**URL:** https://platform.k12-ai-infrastructure.org/competitions/3/
**Report compiled from official pages:** Home, Problem Description, About, Official Rules, Code Submission Format, Publication Bonus (Community Code and FAQ were not independently linked as separate content pages beyond navigation; Community Code is a leaderboard-adjacent code-sharing area, not a separate ruleset)

> ⚠️ Note on scope: The site did not expose a separate stand-alone "FAQ" page in the navigation — only Home, Problem description, Code submission format, Publication bonus, About, Official rules, Leaderboard, and Community code. Where the prompt asked for FAQ content, **the rules do not specify a separate FAQ page**; questions are instead directed to the competition forum and email.

---

## SECTION 1 — Executive Summary

- **Goal:** Predict whether a student will answer a follow‑up assessment question correctly after a tutoring session, using only the student–tutor conversation transcript (and a short learning-objective description) — a proxy for whether real learning occurred during the session.
- **Input:** Per-response metadata (`response_id`, `session_id`, `learning_objective`) plus a per-session transcript CSV (`session_id`, `utterance_id`, `role`, `content`, `timestamp`) containing turn-by-turn tutor/student dialogue.
- **Output:** A CSV with `response_id` and a predicted `probability` (0–1) that the student answered the next question correctly.
- **Evaluation metric:** Log loss (lower is better), with ROC AUC shown on the leaderboard for reference only — it does not affect ranking.
- **What organizers actually care about:** This is explicitly *not* a pure leaderboard-accuracy competition. Prizes are awarded on a **combination of leaderboard performance and a written solution "insight" report**, judged on whether the work surfaces generalizable, actionable insight into tutoring effectiveness and knowledge tracing — not just predictive accuracy.
- **What makes a strong solution:** A model that (1) draws its signal primarily from the *conversation transcript* rather than shortcuts like the learning-objective text alone, (2) is well calibrated (since the metric is log loss), and (3) is paired with a clear write-up identifying interpretable tutoring patterns, feature importance, and generalizability across the two data sources (Eedi and Third Space Learning).

---

## SECTION 2 — What IS Allowed (Detailed Checklist)

| Technique | Status | Rule basis / explanation | Source page |
|---|---|---|---|
| Pretrained models (general) | ✔ Allowed, with license condition | External data/models are allowed provided they are "publicly available and openly licensed." To be prize-eligible, licensing must permit release for broad use, including commercial use (no NC/CC-BY-NC licenses) | Home / Problem description |
| BERT, ModernBERT, RoBERTa, DeBERTa, other HF encoder models | ✔ Conditional | Allowed as pretrained/external models if openly licensed for commercial use; several are pre-loaded in `huggingface_models/` in the runtime, meaning no internet is even needed to fetch them | Code submission format |
| LLM embeddings / Sentence-Transformers | ✔ Conditional | Same external-model rule applies; must be open-licensed (e.g., MIT/Apache-2/CC0/CC-BY) for prize eligibility | Rules |
| HuggingFace checkpoints generally | ✔ Conditional | Allowed if license permits commercial reuse; the runtime documentation lets you request additional HF models be pre-loaded since there's no live internet access | Code submission format |
| Fine-tuning / LoRA / PEFT | ✔ Allowed | Not prohibited anywhere in the rules; this is standard model development, only subject to the "no test-set information leakage" rule and open-license requirement on any pretrained base weights used | Rules |
| External datasets | ✔ Conditional (Open External Data) | The competition uses the "Open External Data" rule: external data (including pretrained models) may be used if freely and publicly available under a permissive open license that doesn't prohibit commercial use (e.g., CC0, CC-BY) | Rules |
| Feature engineering | ✔ Encouraged | The problem description explicitly frames feature engineering from the high-dimensional transcript data as a core research question of the challenge | Problem description |
| Ensembling | ✔ Allowed | No restriction; standard technique, subject to runtime/time limits | Code submission format |
| Cross-validation | ✔ Encouraged | Explicitly called out as a desired methodological element in both the modeling write-up template and the Publication Bonus evaluation criteria | Problem description / Publication bonus |
| Calibration | ✔ Encouraged | Because scoring is log loss, the rules explicitly note that log loss can often be improved through calibration | Problem description |
| Pseudo-labeling on the *test* set | ❌ Not allowed | See Section 3 — precluded by the "use of test data" independence rule | Rules |
| Pseudo-labeling on *training* data only | ✔ Conditional | Participants may annotate provided training data as long as annotations are included with the solution for reproduction and don't overfit to the test set | Rules |
| Data augmentation | ✔ Allowed | Not restricted, so long as any external material used for augmentation meets the open-license external-data rule | Rules |
| OCR | ✔ Allowed (not directly relevant) | No text in the rules restricts OCR; the data is already transcribed text, so this is a non-issue but not prohibited | Problem description |
| RAG (retrieval-augmented generation) | ✔ Conditional | Allowed only if all retrieved/reference data is either open-licensed external data or the competition's own training data — **no internet access is available at inference time**, so any retrieval corpus must be packaged with the submission | Code submission format |
| Prompting (e.g., using an LLM to score/tag transcripts) | ✔ Conditional | Allowed if the model weights are packaged in the submission (no network access in the runtime); using an LLM checkpoint requires it be present in `huggingface_models/` or bundled in your archive | Code submission format |
| Knowledge distillation | ✔ Allowed | Not restricted | Rules |
| Quantization / ONNX / TensorRT | ✔ Allowed | Not restricted; useful for meeting the 6-hour runtime and 60GB size limits | Code submission format |
| GPU inference | ✔ Allowed | The runtime provides one NVIDIA A100 GPU (80GB VRAM) | Code submission format |
| CPU inference | ✔ Allowed | The container provides 24 vCPUs (AMD EPYC 7V13) and 220GB RAM; code must run inside the GPU-enabled container even if computation is CPU-bound | Code submission format |
| Manual annotation of **training** data | ✔ Conditional | Permitted if included with the solution to enable reproduction, and doesn't overfit to the test set | Rules |
| Publicly sharing code | ✔ Conditional | Permitted, but publicly shared code is automatically deemed MIT-licensed by the act of sharing | Rules |

---

## SECTION 3 — What is NOT Allowed

- **Internet access during inference:** The code-execution container has **no network access**. All model weights, dependencies, and any retrieval corpora must be bundled in the submission archive or drawn from the pre-loaded `huggingface_models/` directory.
- **Use of test-set information across samples ("test-time training," pseudo-labeling on test data, unsupervised learning on the test set):** Each test sample must be processed independently at inference; the rules state this "precludes using information gathered across multiple test samples as feature inputs or target labels for model training." Running the same training code with a different test set (or none) must produce identical model weights — i.e., no adaptation to the test set is allowed.
- **Manual annotation of the *test* set:** Explicitly forbidden — "Participants may not add any manual annotations to the provided test data."
- **Printing/logging test-set content:** The submission requirements explicitly prohibit printing or logging *any* information about the test dataset — including transcript excerpts, learning-objective text, or aggregate statistics like sums, means, or token counts — and state this may be grounds for disqualification under the test-data-independence rule.
- **Private data not shareable with organizers:** External data may be used, but even non-public external data must be capable of being shared with the organizers on request for verification; wholly private/unverifiable data used to build a prize-eligible model is a problem.
- **Non-commercial-only licenses (NC / CC-BY-NC) on any external data or model, for prize eligibility:** Explicitly disallowed for prize eligibility — "no NC, CC NC, or CC BY‑NC licenses."
- **Multiple accounts / multi-accounting:** Only one platform account per person is allowed; using more than one is deemed cheating and can result in disqualification and account banning.
- **Private sharing of code or data outside your team:** Prohibited; public sharing is allowed (and is deemed to auto-license the shared code under MIT).
- **Exceeding submission limits:** Number of submissions is capped (three full submissions per week); attempts to circumvent this trigger disqualification.
- **Non-Python-3.12 submissions:** "All submissions for inference must run on Python 3.12. No other languages or versions of Python are supported."
- **Submissions exceeding runtime/size limits:** 6-hour hard cap for full submissions (10 minutes for smoke tests), 60GB archive size cap.
- **Root filesystem access, writing outside the designated output path, or modifying the read-only data folder:** Not permitted by the runtime design (no root access; data folder is read-only).
- **Legal entities/organizations entering (only natural persons eligible), participants under 18, residents of OFAC-sanctioned countries, and individuals in the Russian Federation:** All ineligible to win prizes per the eligibility section.
- **Previously published/awarded submissions, plagiarized or infringing content, malicious code:** All barred by the standard submission warranties.

---

## SECTION 4 — External Models

| Model | Status | License condition | Notes |
|---|---|---|---|
| ModernBERT | CONDITIONAL — Yes | Must be openly licensed for commercial use to be prize-eligible (Apache-2.0 satisfies this) | Not explicitly named on the site; governed by the general external-model rule |
| DeBERTa-v3 | CONDITIONAL — Yes | Microsoft's DeBERTa-v3 is MIT-licensed, which satisfies the open/commercial-use requirement | General rule applies |
| RoBERTa | CONDITIONAL — Yes | MIT-licensed by Meta/FAIR — satisfies requirement | General rule applies |
| BGE (BAAI embeddings) | CONDITIONAL — Yes, check specific checkpoint license | Must confirm the specific BGE variant's license permits commercial use | General rule applies |
| E5 embeddings | CONDITIONAL — Yes, check specific checkpoint license | Same as above | General rule applies |
| Qwen | CONDITIONAL | Some Qwen releases carry usage restrictions (e.g., limits above certain user thresholds); participants must verify the exact checkpoint's license permits unrestricted commercial re-release | Rules explicitly require proof of license on request |
| Llama | CONDITIONAL | Meta's Llama license includes acceptable-use and scale-based restrictions that are **not** a fully open license in the CC0/CC-BY/MIT/Apache sense — participants should ask organizers before relying on it for a *prize-eligible* submission | Ask via forum/email per rules |
| Gemma | CONDITIONAL | Google's Gemma terms include use restrictions beyond a standard open-source license — verify against the "no NC" and "broad commercial use" requirement | Ask organizers if unsure |
| Mistral | CONDITIONAL — Yes for Apache-2.0 releases | Many Mistral models are Apache-2.0 (fully open); some later/instruct variants may carry different terms — check the specific checkpoint | General rule applies |
| Phi (Microsoft) | CONDITIONAL — Yes | Recent Phi models are MIT-licensed | General rule applies |
| OpenAI embeddings (API-based) | ❌ Effectively NO for prize eligibility, and NO for inference regardless | The runtime has no internet access at inference, so a hosted API-only model cannot be called during scoring; separately, OpenAI's embeddings are not open-licensed/redistributable weights, so they fail the "open license enabling broad reuse" requirement | Code submission format (no network access) |
| Sentence Transformers (the library and many of its published checkpoints) | ✔ Yes | Several sentence-transformers checkpoints are already pre-loaded in the runtime's `huggingface_models/` directory (the example given is `sentence-transformers/all-MiniLM-L6-v2`), and the library/most checkpoints are Apache-2.0 | Code submission format |
| HuggingFace checkpoints generally | CONDITIONAL | Governed entirely by each checkpoint's individual license — the rule is model-license-agnostic to "HuggingFace" as a platform; what matters is the specific model card's license | Rules |

**General licensing requirement (applies to all of the above):** To be **eligible for prizes**, any external model's license must allow the resulting model to be released for broad use, including commercial purposes — this explicitly rules out NC/CC-BY-NC-style licenses. The Home page states finalists must formally declare all external data/models used and either certify commercial-use licensing or opt out of prize eligibility.

---

## SECTION 5 — External Data

| Data Source | Status | Rule / Explanation |
|---|---|---|
| Kaggle datasets | CONDITIONAL | Only usable if the specific dataset's license is a permissive open license (CC0, CC-BY, MIT, etc.) that doesn't prohibit commercial use — many Kaggle datasets carry mixed or unclear licenses, so each one must be checked individually |
| GitHub datasets | CONDITIONAL | Same standard: must carry an explicit open license compatible with commercial use |
| Common Crawl | ✔ Generally Yes | Common Crawl's own terms are broadly permissive, but any derivative or curated subset used should still be checked for its own stated license |
| Wikipedia | ✔ Yes | CC-BY-SA / GFDL — compatible with the "open license, commercial use allowed" standard (note: CC-BY-SA requires share-alike attribution on derivatives) |
| OpenWebText | CONDITIONAL | Depends on the specific redistribution's license terms; participants should verify before using it as an eligibility-affecting resource |
| Educational datasets (general) | CONDITIONAL | Must independently satisfy the open, commercial-use-permitting license standard; the rules do not name specific approved third-party educational datasets |
| Generated synthetic data (self-generated, e.g. via your own scripts/rules) | ✔ Yes, with disclosure | Synthetic data you generate isn't "external data" from a third party per se, but if it's produced using an external model, that model's license still governs; also falls under "Participants may annotate provided training data as long as they are included with solutions to enable reproduction" |
| ChatGPT-generated data | CONDITIONAL | Using outputs from a proprietary LLM (like ChatGPT) as augmented training data is not itself forbidden, but (a) OpenAI's usage terms should be checked for redistribution restrictions, and (b) it must not touch the *test* set (which must remain unannotated and used only as provided) |
| Teacher-created data | CONDITIONAL | Any manually created/annotated data is allowed **only for training data**, must be included with the solution for reproducibility, and must not be used to hand-annotate or otherwise touch the *test* set |

**Underlying rule for all rows above (External Data Rule: "Open External Data"):** Participants may use external data other than the competition data, including pretrained models, provided it is "freely and publicly available to all Participants under a permissive open license... that does not prohibit commercial use (e.g., CC0 or CC-BY)." Where legal right to use data exists but it isn't fully public, the "External Data With Rights" fallback still requires participants be able to furnish proof of license to organizers on request — however, the Home page's specific guidance for *this* competition emphasizes the open/commercial-reuse standard as the bar for **prize eligibility**.

---

## SECTION 6 — Submission Rules

- **Format:** A `.zip` archive (e.g., `submission.zip`) containing a `main.py` at the **root level** (no enclosing folder) plus any needed `assets/` (model weights, etc.).
- **What `main.py` does:** Reads `data/test_features.csv` and `data/test_transcripts/`, performs inference, and writes `submission.csv` (columns: `response_id`, `probability`) back to the same root directory.
- **Runtime/time limits:** 6 hours max for a full submission; 10 minutes max for a smoke test.
- **Submission cadence limits:** 3 full submissions per week; smoke tests and cancelled/failed jobs don't count against the limit.
- **Memory / compute:** 24 vCPUs (AMD EPYC 7V13), 220GB RAM, 1× NVIDIA A100 GPU with 80GB VRAM.
- **Package/archive size limit:** Should not exceed 60GB total (code + model assets); larger submissions are likely to fail (the site notes this limit may be raised in future).
- **Container/offline restrictions:** The container has **no network access** at inference — all code, packages, and model weights must be pre-packaged or drawn from the pre-loaded `huggingface_models/` directory; there is also **no root filesystem access**.
- **Smoke test:** A lightweight test environment using the same data structure but only ~100 responses sampled from the *training* set (not the real test set), meant to catch bugs before a full submission.
- **Logging limits:** Output during execution is capped at 500 lines, 500 characters per line — and must never print/log test-set content (see Section 3).
- **Required files / folder structure:**
  ```
  submission root directory
  ├── assets/         (all assets needed for inference, e.g., model weights)
  └── main.py         (inference script; must sit at the root, not nested)
  ```
- **Python version:** Python 3.12 only, using packages defined in the linked GitHub runtime repository (built on `uv`, PyTorch, and vLLM with CUDA 12.9). Additional package requests can be filed as GitHub issues in that repository.

---

## SECTION 7 — Licensing

**Two distinct licensing regimes apply, and it's important not to conflate them:**

1. **Winner License Type — for *your own submitted solution/code* if you win a prize:** Must be released under **The MIT License**. Any additional software your solution depends on must also be under an open-source license that doesn't prohibit free commercial use, so the whole solution is reproducible using only free, open-source components.
2. **External Data / Model Rule — for *third-party resources* you use as inputs:** Governed by the "Open External Data" rule — the external resource itself (dataset or pretrained model) must carry a permissive open license that doesn't prohibit commercial use.

| License | Accepted? | Notes |
|---|---|---|
| MIT | ✔ Accepted | This is the *required* license for your own winning submission code |
| Apache-2.0 | ✔ Accepted | Satisfies "open source license that does not prohibit free commercial use" for dependencies/external models |
| BSD (2/3-clause) | ✔ Accepted | Same rationale as Apache-2.0 |
| CC0 | ✔ Accepted | Explicitly named as an example acceptable external-data license |
| CC-BY | ✔ Accepted | Explicitly named as an example acceptable external-data license |
| CC-BY-SA | ✔ Likely accepted with care | Not explicitly named, but is an open, commercial-use-permitting license; share-alike obligations on any redistributed derivative should be honored |
| GPL (v2/v3) | ⚠ Conditional / Risky | GPL is technically an open-source license permitting commercial use, but its copyleft (viral) terms may conflict with the requirement that your *own* winning solution be released under plain MIT — mixing GPL dependencies into an MIT-licensed solution can create legal friction. Not explicitly addressed by the rules; **the rules do not specify** how GPL interacts with the MIT winner requirement, so this should be confirmed with organizers before relying on it |
| CC-BY-NC / any "NC" (non-commercial) license | ❌ Rejected for prize eligibility | Explicitly excluded: "no NC, CC NC, or CC BY-NC licenses" for external data/models used in a prize-eligible solution |
| Proprietary / closed, no redistribution rights (e.g., raw OpenAI API-only models) | ❌ Rejected | Fails both the open-license standard and the no-internet-access runtime constraint |

---

## SECTION 8 — Winning Strategy (Derived Only From the Official Rules)

Because prizes are awarded on **leaderboard performance + write-up quality** (not leaderboard rank alone), and the top 15 teams by leaderboard are the only ones eligible to submit write-ups, the winning strategy has two equally weighted tracks:

- **Best NLP modeling approach:** Given (a) log loss as the metric, (b) no internet access at inference, and (c) pre-loaded sentence-transformer/HF checkpoints in the runtime, a practical strong baseline is a transformer encoder (e.g., an MIT/Apache-2-licensed DeBERTa-v3 or a Sentence-Transformers embedding model already available in `huggingface_models/`) fine-tuned or fit on top of transcript embeddings, with careful attention to open licensing so the approach remains prize-eligible.
- **Best feature engineering:** The problem description explicitly flags this as a central research question — extracting generalizable features from long, high-dimensional transcripts, identifying discrete "tutoring moves," and finding "key moments" in long Third Space Learning transcripts that carry outsized predictive signal. This is *rewarded directly* in the write-up rubric under "Relevance" and "Rigor."
- **Best ensemble strategy:** Not directly specified by the rules, but permitted; combining a transcript-embedding model with structured/engineered features (turn counts, tutoring-move tags, session length, etc.) fits both the metric (log loss favors well-calibrated probability blends) and the qualitative goal (interpretable, decomposable signal for the write-up).
- **Best validation strategy:** Because the leaderboard has a public/private split and the training data spans two structurally different providers (Eedi's short chat sessions vs. Third Space Learning's long voice-transcribed sessions), a validation scheme that holds out **by session/provider** — rather than a naive random split — will better estimate generalizability, which is explicitly rewarded under the "Generalizability" criterion (35% of write-up score).
- **Best calibration method:** The rules explicitly call out that log loss "can often be improved with calibration," linking to scikit-learn's calibration module — so applying isotonic regression or Platt scaling on a held-out fold is directly incentivized by the metric itself.
- **Best explainability methods:** The write-up template and the Publication Bonus criteria both explicitly ask for **interpretability** — the write-up template calls for identifying "especially informative modeling features," and the Publication Bonus rubric explicitly recommends interpretability frameworks such as SHAP, LIME, or counterfactual explanations under "Methodological Rigor."

**Why this combination wins:** The rules are unusually explicit that raw leaderboard score is *not* sufficient — the judges combine leaderboard rank with write-up quality weighted on Relevance (35%), Generalizability (35%), Communication (15%), and Rigor (15%). A team with a slightly lower log loss but a rigorous, interpretable, well-validated write-up connecting model behavior to real tutoring pedagogy is explicitly favored by this rubric over a black-box leaderboard-topping model with no insight.

---

## SECTION 9 — Hidden Pitfalls (Rules Competitors Often Miss)

- **Logging test-set statistics is a disqualification risk**, not just a style issue — even aggregate stats like token counts or means computed on test data are explicitly prohibited, not just raw transcript excerpts.
- **Only the top 15 leaderboard teams can win any prize at all** (including the top 3 cash prizes) — being 16th or lower on the leaderboard makes you ineligible for prizes regardless of write-up quality, since write-up submission itself is gated behind top-15 leaderboard placement.
- **The write-up has a hard 4-page limit (excluding references)**, with strict formatting: 8.5×11" pages, 1" margins, minimum 11pt body text / 10pt in tables and figures, minimum single-line spacing — a poorly formatted or over-length write-up risks direct point loss.
– **Winning solutions must independently be released under MIT**, separate from — and in addition to — any external-model license conditions; a team using otherwise-compliant open-licensed external models could still fail the winner requirement if their *own* code depends on a non-MIT-compatible open license (e.g., certain copyleft GPL components).
- **External data doesn't need to be public, but it does need to be shareable with organizers on request** to enable independent verification — a private dataset you have legal rights to may still disqualify you from *prizes* (though not from competing) if you can't produce it, or if its license isn't broad enough to cover the released model.
- **Prize finalists must proactively declare all external data/models used** and either certify open, commercial-compatible licensing or voluntarily opt out of prize eligibility — silence or failure to disclose is treated as a compliance risk, not neutral.
- **The Publication Bonus track has its own separate, stricter requirements**: double-blind anonymization (no author names, affiliations, or self-citation in first person), a 7,000–10,000 word main text, and a mandatory AI-use disclosure statement if generative AI tools were used for substantive manuscript editing (though basic grammar/spell-check tools are exempt from disclosure).
- **Smoke tests use *training* data, not real test data** — passing the smoke test only confirms your code runs correctly on 100 sampled *training* responses, not that it will perform well or run within time on the true (larger) private test set.
- **Data is provided per-response, and a single tutoring session can generate multiple samples** (one per learning objective covered) — models that leak information across responses tied to the same session_id risk violating the sample-independence requirement, since the rule requires each *test* sample processed independently.
- **The learning-objective description alone is explicitly discouraged** as a modeling shortcut — the problem description twice states strong solutions should draw primarily from the conversation transcript, not the objective text, and the write-up rubric explicitly disqualifies "how to predict probability of correctness based on inferred difficulty of the learning objective description, without reference to the session transcript" as an uninteresting finding.

---

## SECTION 10 — Final Checklist Tables

### ✅ Table 1 — Allowed
| Item | Condition |
|---|---|
| Pretrained/open-licensed HF models (DeBERTa, RoBERTa, Sentence-Transformers, Mistral-Apache, Phi, etc.) | Must be openly licensed for commercial reuse for prize eligibility |
| Fine-tuning, LoRA, PEFT | No restriction |
| Feature engineering, ensembling, cross-validation, calibration | Explicitly encouraged |
| Data augmentation and synthetic data generation | Must respect any underlying model's license; training-only |
| Knowledge distillation, quantization, ONNX/TensorRT | No restriction |
| GPU or CPU inference inside the provided container | Must fit 6-hour runtime and 60GB size cap |
| Manual annotation of **training** data | Must be included with solution, must not overfit test set |
| Public code sharing | Automatically MIT-licensed upon sharing |

### ❌ Table 2 — Not Allowed
| Item | Reason |
|---|---|
| Internet access during inference | No network access in the runtime container |
| Manual annotation of the **test** set | Explicitly prohibited |
| Pseudo-labeling / unsupervised learning using the test set | Violates test-sample independence rule |
| Logging/printing test-set content or aggregate stats | Explicit disqualification risk |
| Multiple accounts | Deemed cheating |
| Private sharing of code/data outside your team | Prohibited |
| Non-open/NC-licensed external models or data (for prize eligibility) | Explicitly excludes NC / CC BY-NC |
| Non-Python-3.12 submissions | Only Python 3.12 supported |
| Submissions >60GB or >6-hour runtime | Hard technical limits |

### ⚠ Table 3 — Allowed With Conditions
| Item | Condition |
|---|---|
| External datasets (Kaggle, GitHub, OpenWebText, etc.) | Must carry a permissive open, commercial-use-compatible license |
| Llama, Gemma, Qwen models | Depends on specific checkpoint's license terms — verify against "no NC" standard, confirm with organizers if unsure |
| RAG / retrieval pipelines | Retrieval corpus must be fully packaged in the submission (no live internet) |
| ChatGPT/LLM-generated synthetic training data | Allowed for training only; underlying model's terms of use still apply |
| GPL-licensed dependencies | Not explicitly addressed by the rules; potential conflict with the MIT winner-license requirement — confirm with organizers |
| External data with legal-but-non-public rights | Usable to compete, but must be shareable with organizers on request to remain prize-eligible |

---

## Where Something Is Unclear

- **The rules do not specify** a dedicated FAQ page separate from the competition forum/email contact.
- **The rules do not specify** exactly how a GPL-licensed dependency would be reconciled with the "own solution must be MIT" winner requirement — this is a genuine gray area best resolved by asking the organizers directly.
- **The rules do not specify** a definitive list of "pre-approved" external datasets or models; eligibility is determined case-by-case against the general open/commercial-license standard, with prize finalists required to certify compliance.

---

*All statements above are drawn from the official competition website (`platform.k12-ai-infrastructure.org/competitions/3/` and its Home, Problem Description, About, Official Rules, Code Submission Format, and Publication Bonus pages) as of the date this report was compiled. Because DrivenData/the Sponsor reserve sole discretion to interpret and enforce these rules, and details can be updated on the live site, participants should verify current text on the official pages and consult the competition forum for any edge cases before relying on this report for prize-eligibility decisions.*

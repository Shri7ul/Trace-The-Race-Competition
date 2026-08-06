# Competition Analysis & Compliance Review Report

**Competition Title:** Trace the Ace: Tutoring Outcomes Prediction Challenge

**Platform:** K-12 AI Infrastructure Program (managed by Digital Promise, operated by DrivenData)

**URL:** `[https://platform.k12-ai-infrastructure.org/competitions/3](https://platform.k12-ai-infrastructure.org/competitions/3)`

**Host Organization:** National Tutoring Observatory (NTO) (in partnership with Eedi and Third Space Learning)

**Total Prize Pool:** $50,000 USD

**Competition Deadline:** August 27, 2026, 11:59 p.m. UTC (Model Submissions) | September 15, 2026, 11:59 p.m. UTC (Solution Write-up)

---

## SECTION 1 — Executive Summary

### Goal of the Competition

The core objective of **Trace the Ace** is to evaluate tutoring effectiveness and predict student proximal learning outcomes using **only student–tutor conversation transcripts** and session metadata. Specifically, participants build machine learning models that analyze dialogue history from a tutoring session to predict whether a student will correctly answer a follow-up assessment question on the targeted learning objective.

*Source:* [Problem Description Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/4/) & [Home Page](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/3/)

### Input Data

Participants are provided with dialogue transcripts and response metadata split into training and test sets:

1. **Metadata CSV (`train_features.csv` / `test_features.csv`):**
* `response_id` (`str`): Unique sample identifier.
* `session_id` (`str`): Identifier linking to the session transcript.
* `learning_objective` (`str`): Short description of the concept being taught/tested.


2. **Transcript CSVs (`train_transcripts/{session_id}.csv` / `test_transcripts/{session_id}.csv`):**
* `session_id` (`str`): Session link.
* `utterance_id` (`str`): Order/utterance identifier within the conversation.
* `role` (`str`): Speaker role (`tutor` or `student`).
* `content` (`str`): Transcribed dialogue text (rigorously anonymized with contextually relevant surrogate names).
* `timestamp` (`datetime`): Utterance timestamp.



*Source:* [Problem Description Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/4/) & [About Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/5/)

### Output Data

For every `response_id` in `test_features.csv`, the model must output a probability score ($p \in [0.0, 1.0]$) representing the likelihood that the student answered the follow-up assessment question correctly.

* Required file name: `submission.csv` containing columns `response_id` and `probability`.

*Source:* [Code Submission Format Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/6/)

### Evaluation Metric

* **Primary Leaderboard Metric:** **Log Loss** (Binary Cross-Entropy):

$$\text{LogLoss} = -\frac{1}{N} \sum_{i=1}^{N} \left[ y_i \log(p_i) + (1 - y_i) \log(1 - p_i) \right]$$



where $y_i \in \{0, 1\}$ is the actual correctness label and $p_i$ is the predicted probability.
* **Reference Metric:** **ROC AUC** is displayed on the leaderboard for reference, but **does not** impact leaderboard standing or prize eligibility.

*Source:* [Problem Description Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/4/)

### What Organizers Actually Care About

The organizers (National Tutoring Observatory and DrivenData) explicitly emphasize that **leaderboard rank alone does not determine the winners**.

* The **top 15 teams** on the final leaderboard are invited to submit a **solution write-up (PDF)** by September 15, 2026.
* Final winners (1st–3rd place) are selected based on a **combination of leaderboard performance and write-up quality**.
* Organizers prioritize discovering **generalizable insights into tutoring mechanisms and educational science** over pure "black-box" over-optimization. Key research questions include:
1. *What tutoring moves or dialogue dynamics best indicate learning?*
2. *How can key moments in long transcripts be extracted?*
3. *Which components of the model generalize across different contexts/providers (Eedi vs. Third Space Learning)?*



*Source:* [Home Page](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/3/) & [Problem Description Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/4/)

### What Makes a Strong Solution

1. **Calibrated Probabilities:** Because the metric is Log Loss, confident incorrect predictions carry heavy penalties. Calibrated output (via Platt scaling, Isotonic regression, or temperature scaling) is essential.
2. **Context-Aware Dialogue Processing:** Leveraging local NLP/LLM models that effectively process long multi-turn dialogues, speaker roles (`tutor` vs. `student`), temporal cadence, and learning objective semantics.
3. **Robust Cross-Validation:** Avoiding data leakage across turns or sessions by grouping splits strictly by `session_id`.
4. **Actionable Insights & Interpretability:** High-quality feature extraction, SHAP/LIME explainability, and pedagogical turn classifications that yield a compelling academic write-up and preprint for the $2,000 Publication Bonus.

---

## SECTION 2 — What IS Allowed (Checklist & Compliance Analysis)

| Technique / Method | Allowed? | Official Rule / Citation | Explanation & Conditions |
| --- | --- | --- | --- |
| **Pretrained Models** | ✔ Allowed | *"Participants may use external data other than the competition data, including pre-trained models... provided that the external data is freely and publicly available under a permissive open license that does not prohibit commercial use."* ([Official Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/)) | Must have open commercial licenses (e.g., Apache 2.0, MIT) and be packaged in `submission.zip` or pre-loaded in `huggingface_models/`. |
| **BERT / ModernBERT / RoBERTa / DeBERTa** | ✔ Allowed | *"Participants may use pre-trained models..."* ([Official Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/)) | Standard transformer backbones with open commercial licenses are fully allowed for offline feature extraction and fine-tuning. |
| **LLM Embeddings / Sentence Transformers** | ✔ Allowed | *"huggingface_models/ makes some pre-loaded HuggingFace model weights available... e.g., sentence-transformers/all-MiniLM-L6-v2"* ([Code Submission Format Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/6/)) | Sentence Transformers and local embedding models are explicitly supported both in the runtime environment and as offline pretrained assets. |
| **Fine-tuning / LoRA / PEFT** | ✔ Allowed | *"Create and train your own model... package your trained model and prediction code for evaluation"* ([Home Page](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/3/)) | Models can be fine-tuned offline on local GPUs. Weights/adapters (LoRA) must be bundled into `submission.zip`. |
| **External Datasets** | ✔ Allowed | *"Participants may use external data... provided that the external data is freely and publicly available to all Participants under a permissive open license that does not prohibit commercial use."* ([Official Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/)) | Allowed if publicly available to everyone under commercial-friendly terms (e.g., CC0, CC-BY, Apache 2.0). |
| **Feature Engineering** | ✔ Allowed | *"What can you learn from trying different approaches to feature engineering? In this high-dimensional data, how can you extract generalizable features?"* ([Problem Description Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/4/)) | Organizers explicitly encourage extracting linguistic, temporal, conversational, and pedagogical features. |
| **Ensembling** | ✔ Allowed | Standard DrivenData competition practice | Multiple offline models can be combined inside `main.py` provided total execution stays within the 6-hour time limit. |
| **Cross Validation** | ✔ Allowed | *"We encourage... robust cross-validation techniques."* ([Publication Bonus Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/8/)) | Recommended for local offline validation. Grouping by `session_id` is crucial. |
| **Probability Calibration** | ✔ Allowed | *"Log loss can often be improved with calibration. A well-calibrated model outputs predictions that are directly interpretable as probabilities."* ([Problem Description Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/4/)) | Highly recommended by organizers to optimize the Log Loss objective. |
| **Pseudo Labeling (on Train/External Data)** | ✔ Allowed | Standard semi-supervised learning on training/public external datasets. | Allowed on training or public external data. **NOT allowed on test set during inference**. |
| **Data Augmentation** | ✔ Allowed | Standard model training practice. | Synthetic paraphrasing or back-translation applied to training data offline prior to submission. |
| **Knowledge Distillation** | ✔ Allowed | Standard model training practice. | Distilling insights or soft labels from a large local LLM into a faster encoder (e.g., DeBERTa/ModernBERT) for containerized inference. |
| **Prompting / Local LLMs** | ✔ Allowed | *"Request pre-loaded Hugging Face models (Qwen2.5-14B, Mistral-Small-24B-2501...)"* ([Runtime Repository](https://github.com/drivendataorg/tutoring-outcomes-runtime)) | Local, offline LLMs can be prompted inside the container environment. |
| **Quantization (ONNX, TensorRT, GGUF, AWQ, vLLM)** | ✔ Allowed | Container runtime environment supports GPU execution. | Quantizing models (e.g., INT8/INT4, ONNX) is fully allowed and beneficial for adhering to memory and time limits. |
| **GPU / CPU Inference** | ✔ Allowed | Containerized cloud compute environment ([Code Submission Format Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/6/)) | Execution runs in a container with GPU and CPU resources. |

---

## SECTION 3 — What is NOT Allowed

### 1. Internet Access During Inference

* **Rule:** *"There will be no network access inside the runtime environment."* ([Code Submission Format Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/6/))
* **Explanation:** All code, dependencies, and model weights must execute completely offline within the container. Calling external APIs (e.g., OpenAI, Anthropic, HuggingFace Hub) during container execution will fail.

### 2. Test-Time Training / Transductive Learning / Test Set Pseudo-Labeling

* **Rule:** *"Unless otherwise specified on the website, each test data sample should be processed independently during inference without the use of information from other cases in the test set. By default, this precludes using information gathered across multiple test samples as feature inputs or target labels for model training, for instance through pseudo labeling or unsupervised learning on the test set."* ([Official Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/))
* **Explanation:** Running inference on Sample A cannot depend on statistics, embeddings, or labels calculated from Sample B in the test set. Model parameters and fitted feature scalers must remain completely static during test set execution.

### 3. Printing or Logging Test Set Data

* **Rule:** *"Submission does NOT print or log any information about the test dataset, including excerpts of transcripts, learning objective descriptions, and/or aggregations such as sums, means, or token counts. Doing so may be grounds for disqualification."* ([Code Submission Format Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/6/))
* **Explanation:** Logging stdout/stderr is monitored. Exposing test set characteristics via container logs violates the sample independence rule and leads to instant disqualification.

### 4. Multiple Accounts

* **Rule:** *"You cannot sign up to the K-12 AI Infrastructure platform from multiple accounts and therefore you cannot submit from multiple accounts... Competing using more than one account per individual is a breach of these Competition Rules."* ([Official Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/))
* **Explanation:** Strict one-person, one-account policy. Sybil accounts result in automatic disqualification for all associated accounts.

### 5. Private Code or Data Sharing Outside Teams

* **Rule:** *"Privately sharing code or data outside of teams is not permitted."* ([Official Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/))
* **Explanation:** Code and data must be developed solely within official registered teams. All shared code must be posted publicly on the official competition forum or Community Code tab.

### 6. Non-Commercial Licensed Models or Data

* **Rule:** *"provided that the external data [and pretrained models] is freely and publicly available to all Participants under a permissive open license that does not prohibit commercial use (e.g., CC0 or CC-BY)."* ([Official Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/))
* **Explanation:** Any asset restricted to non-commercial research use (e.g., CC-BY-NC licenses) is strictly prohibited.

### 7. Proprietary / Private Datasets & Closed Pretrained Models

* **Rule:** *"Participants may use external data other than the competition data... provided that the external data is freely and publicly available to all Participants..."* ([Official Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/))
* **Explanation:** Using private, proprietary, unreleased datasets or non-public model weights that other competitors cannot access is strictly illegal.

### 8. Manual Labeling & Human Intervention

* **Rule:** *"Eligible solutions must be able to run inference on new test data automatically, without retraining the model."* ([Official Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/))
* **Explanation:** Human-in-the-loop inspection or manual adjustments to predictions during containerized execution are prohibited.

---

## SECTION 4 — External Models Assessment

All external models must satisfy two conditions:

1. **License Condition:** Must carry a permissive open-source license that **permits commercial use** (e.g., MIT, Apache 2.0, BSD, CC-BY).
2. **Execution Condition:** Must fit inside the zip submission or pre-loaded runtime environment and run offline within the 6-hour execution limit.

| Model / Family | Status | Compliance Explanation | License Compatibility |
| --- | --- | --- | --- |
| **ModernBERT** | **YES** | Openly licensed (Apache 2.0). Ideal encoder architecture for long context window dialogue processing. | Permissive commercial open license. |
| **DeBERTa-v3** | **YES** | Permissive MIT license. Excellent cross-encoder performance for text classification tasks. | MIT License (Fully compatible). |
| **RoBERTa** | **YES** | Open MIT/Apache license. Lightweight and effective baseline encoder. | Permissive commercial open license. |
| **BGE (BAAI)** | **YES** | Openly released under Apache 2.0. Excellent for embedding text and semantic similarity. | Apache 2.0 (Fully compatible). |
| **E5 (Microsoft)** | **YES** | Open MIT license. Suitable for dense text embeddings. | MIT License (Fully compatible). |
| **Qwen (2.5 Series)** | **YES** | Open weights under Apache 2.0 / Qwen License (permits commercial use for models <100B). | Commercial friendly license. |
| **Llama (Meta Llama 3/3.1)** | **CONDITIONAL / CAUTION** | Meta's Llama Community License allows commercial use under 700M monthly active users, but contains specific acceptable use policies and restrictions. *Verification with organizers recommended if used as primary model.* | Custom commercial license (Requires organizer clearance). |
| **Gemma (Google Gemma 2)** | **YES** | Gemma Terms of Use permit commercial usage and redistributions under terms. | Commercial friendly open license. |
| **Mistral (Mistral 7B / Small)** | **YES** | Released under Apache 2.0. | Apache 2.0 (Fully compatible). |
| **Phi (Microsoft Phi-3/3.5)** | **YES** | Released under MIT License. | MIT License (Fully compatible). |
| **OpenAI Embeddings (API)** | **NO (at inference)** / **CONDITIONAL (for train feature generation)** | Cannot be called during test inference due to disabled internet access. Offline generated synthetic train features are allowed if open-licensed. | N/A (Offline API execution disabled). |
| **Sentence Transformers** | **YES** | Explicitly supported in runtime documentation (`sentence-transformers/all-MiniLM-L6-v2`). | Permissive open license. |
| **HuggingFace Checkpoints** | **YES** | Any public HF checkpoint with an open commercial license (Apache 2.0, MIT, BSD, CC-BY) is permitted. | Must check individual repo licenses. |

---

## SECTION 5 — External Data Rules

External data is governed by the **Open External Data Rule**:

> *"Participants may use external data other than the competition data, including pre-trained models, to develop and test their solutions, provided that the external data is freely and publicly available to all Participants under a permissive open license that does not prohibit commercial use (e.g., CC0 or CC-BY)."*
> — [Official Competition Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/)

| Dataset Source | Allowed? | Rules & Conditions |
| --- | --- | --- |
| **Kaggle Datasets** | **CONDITIONAL** | Allowed **ONLY IF** the dataset is publicly accessible and licensed under an open commercial license (e.g., CC0, CC-BY, Apache 2.0). Datasets marked with non-commercial tags (CC-BY-NC) or private/unlisted Kaggle datasets are **strictly prohibited**. |
| **GitHub Datasets** | **CONDITIONAL** | Must be in a public repository with an explicit permissive open-source license. |
| **Common Crawl** | **YES** | Open public domain dataset. |
| **Wikipedia** | **YES** | Publicly available under CC-BY-SA 4.0 (permits commercial use). |
| **OpenWebText** | **YES** | Openly licensed public web dataset. |
| **Educational Datasets (e.g., Bridge, GSM8k, TalkMoves)** | **CONDITIONAL** | Must check specific licenses! For example, GSM8k (MIT) is **ALLOWED**. Datasets with CC-BY-NC-SA (such as TalkMoves or DrawEduMath) are **PROHIBITED** due to non-commercial clauses. |
| **Generated Synthetic Data** | **YES** | Allowed, provided the synthetic dataset is generated prior to final submission and made freely available under an open commercial license. |
| **ChatGPT / LLM Generated Data** | **YES** | Allowed if generated during offline training/data expansion, complies with OpenAI ToS, and is shared/made available under an open commercial license. |
| **Teacher-Created Data** | **CONDITIONAL** | Must be made publicly available to all participants under an open commercial license before the competition submission deadline. Private teacher notes are forbidden. |

---

## SECTION 6 — Submission Rules & Technical Specifications

### Technical Environment & Package Constraints

* **Python Version:** **Python 3.12 ONLY**.
* **Container Format:** Containerized Docker execution managed via DrivenData runtime container repository.
* **Submission File:** Zip archive named `submission.zip`.
* **Root Requirement:** `main.py` **must exist at the root level** of `submission.zip`.

```
submission.zip (unpacked root)
├── assets/
│   ├── model_weights.pt
│   └── tokenizer_config/
└── main.py              # Entry point execution script

```

### File & Folder Directory Structure during Execution

During container execution, the runtime environment creates the following structure:

```
code_execution/
├── data/ (READ-ONLY)
│   ├── submission_format.csv
│   ├── test_features.csv
│   └── test_transcripts/
│       ├── {session_id_1}.csv
│       └── ...
├── huggingface_models/ (PRE-LOADED ASSETS)
│   └── {org}/{model_name}/
├── main.py (EXECUTED AT ROOT)
├── assets/
└── submission.csv (OUTPUT GENERATED BY MAIN.PY)

```

### Limits & Benchmarks

* **Execution Time Limit:**
* **Full Competition Submission:** **6 hours** total runtime.
* **Smoke Test Submission:** **10 minutes** total runtime (evaluates on a 100-sample slice from training set).


* **Submission Frequency:** Limited to **3 full submissions per week**. Failed jobs, cancelled jobs, and smoke tests do **not** count against the weekly submission cap.
* **Logging Constraint:** Maximum of **500 lines of output**, with a maximum of **500 characters per line**.
* **Network Access:** **Strictly Offline (0 network calls permitted)**.

---

## SECTION 7 — Licensing Requirements

### Accepted Licenses

1. **Winning Code License:** Winning solutions (1st–3rd place) **must be released under The MIT License**.
2. **Third-Party Software Dependencies:** Must be available under open-source software licenses that permit free commercial re-use.
3. **External Data & Pretrained Models:** Must be licensed under permissive open licenses that permit commercial re-use:
* **MIT License**
* **Apache 2.0**
* **BSD (2-Clause / 3-Clause)**
* **Creative Commons Zero (CC0 / Public Domain)**
* **Creative Commons Attribution (CC-BY 4.0)**



### Rejected / Prohibited Licenses

* **CC-BY-NC / CC-BY-NC-SA:** Non-commercial restriction explicitly violates the requirement for commercial re-use.
* **GPL v2 / v3 (Copyleft):** Forbidden if bundled in winning code unless compatible with MIT relicensing requirements without imposing copyleft obligations on the host platform.
* **Proprietary / Closed / Non-Redistributable Licenses:** Prohibited.

---

## SECTION 8 — Winning Strategy & Methodology Guidelines

Based strictly on the official rules, problem formulation, and evaluation metrics, here is the optimal research architecture:

```
[ Transcript Data & Metadata ]
               │
               ▼
┌──────────────────────────────┐
│  GroupKFold Cross-Validation  │ ──► (Grouped strictly by session_id)
└──────────────┬───────────────┘
               │
               ├─────────────────────────────────────────┐
               ▼                                         ▼
┌──────────────────────────────┐        ┌──────────────────────────────┐
│ Context-Aware Dialogue Encoders│        │  Pedagogical & Structural    │
│ (DeBERTa-v3 / ModernBERT)     │        │  Feature Extraction          │
└──────────────┬───────────────┘        └──────────────┬───────────────┘
               │                                         │
               └───────────────────┬─────────────────────┘
                                   ▼
                       ┌─────────────────────────┐
                       │  LightGBM / CatBoost &  │
                       │  Neural Classifier      │
                       └───────────┬─────────────┘
                                   ▼
                       ┌─────────────────────────┐
                       │ Probability Calibration │ ──► (Platt Scaling / Temperature)
                       └───────────┬─────────────┘
                                   ▼
                       ┌─────────────────────────┐
                       │ Final Log Loss Optim    │
                       └─────────────────────────┘

```

### 1. Model Architecture

* **Primary Encoders:** Fine-tuned **DeBERTa-v3-large** or **ModernBERT-large**. ModernBERT's native support for long sequence lengths (8k tokens) makes it ideal for handling long multi-turn tutoring dialogues without truncation loss.
* **Backbone Integration:** Concatenate utterance content prefixed by role tags (`[TUTOR]: ... [STUDENT]: ...`) along with the target `learning_objective`.

### 2. Feature Engineering

* **Turn-Taking Dynamics:** Ratio of student-to-tutor speech turns, average utterance length, response latency (calculated from `timestamp` delta).
* **Pedagogical Move Features:** Proportion of tutor utterances that are questions vs. explanations vs. feedback/affirmations.
* **Student Progress Signals:** Sentiment trajectory across turns, linguistic complexity changes, and keyword overlap between student responses and the `learning_objective`.

### 3. Validation Strategy

* **GroupKFold (k=5 or k=10) grouped strictly on `session_id**`.
* *Rationale:* A single tutoring session can produce multiple records across different learning objectives. Splitting session records across train and validation splits would cause severe data leakage and overfit estimates.

### 4. Calibration Method

* **Temperature Scaling** or **Isotonic Regression / Platt Scaling** fitted on out-of-fold validation logits.
* *Rationale:* The evaluation metric is Log Loss, which heavily penalizes uncalibrated overconfident probabilities.

### 5. Explainability Methods (Crucial for Write-Up & Prize Selection)

* **SHAP (SHapley Additive exPlanations)** and **Integrated Gradients** to highlight which exact dialogue turns and tutor strategies contributed to predicted student success.
* *Rationale:* Solution write-up quality and Publication Bonus evaluation directly score papers on identifying predictive mechanisms and educational interpretability.

---

## SECTION 9 — Hidden Pitfalls & Disqualification Risks

1. **Logging Test Set Information:**
*Pitfall:* Printing transcript strings, token lengths, or dataframe summaries during inference.
*Risk:* Automatic disqualification for violating the test sample independence rule.
2. **Incorrect File Structure in `submission.zip`:**
*Pitfall:* Zipping a root folder containing `main.py` rather than zipping `main.py` at the top level of the archive.
*Risk:* Runtime failure (`main.py` not found) wasting a submission slot.
3. **Exceeding Weekly Submission Cap:**
*Pitfall:* Making 3 unverified full submissions early in the week without testing in the smoke test environment.
*Risk:* Inability to submit refined models before the weekly reset.
4. **Using Non-Commercial External Data or Models:**
*Pitfall:* Using popular educational datasets licensed under CC-BY-NC-SA (e.g., TalkMoves).
*Risk:* Disqualification during winning code audit.
5. **Ignoring the Solution Write-up:**
*Pitfall:* Achieving Top 15 on the leaderboard but failing to submit a high-quality PDF write-up by September 15, 2026.
*Risk:* Forfeiture of all prize eligibility (Prizes are awarded based on Leaderboard + Write-up combination).
6. **Failing to Calibrate Output Probabilities:**
*Pitfall:* Outputting raw uncalibrated model probabilities or sigmoid outputs with extreme values (near 0.0 or 1.0).
*Risk:* Massive Log Loss penalties on misclassified confident edge cases.

---

## SECTION 10 — Final Compliance Checklist

### Table 1: ✅ Allowed Techniques & Practices

| Item | Condition / Citation |
| --- | --- |
| **DeBERTa-v3 / ModernBERT / RoBERTa** | Permissive open commercial license ([Official Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/)) |
| **Sentence Transformers / Local Embeddings** | Pre-loaded in `huggingface_models/` or bundled ([Code Submission Format Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/6/)) |
| **GroupKFold Cross-Validation** | Grouped by `session_id` offline during local model training |
| **Local LLM Prompting & Quantization** | Bundled offline or pre-loaded, executing within 6h limit |
| **Probability Calibration** | Encouraged to minimize Log Loss ([Problem Description Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/4/)) |
| **Local Feature Engineering** | Linguistic, temporal, and utterance-level metadata extraction |
| **Model Ensembling** | Combined inside `main.py` offline within container resource limits |
| **Local Smoke Testing** | Free testing using 10-minute smoke test environment |

---

### Table 2: ❌ Not Allowed Practices

| Item | Reason for Prohibition / Citation |
| --- | --- |
| **Internet Access During Inference** | Container environment has 0 network access ([Code Submission Format Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/6/)) |
| **Test Set Pseudo-Labeling / Transductive Learning** | Each test sample must be processed independently ([Official Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/)) |
| **Printing / Logging Test Set Data** | Explicitly prohibited; causes disqualification ([Code Submission Format Page](https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/page/6/)) |
| **Multiple Platform Accounts** | Strictly prohibited; results in ban ([Official Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/)) |
| **Private Code / Data Sharing** | Forbidden outside official registered team members ([Official Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/)) |
| **Non-Commercial Licensed Assets (CC-BY-NC)** | Assets must allow commercial re-use ([Official Rules](https://www.google.com/search?q=https://platform.k12-ai-infrastructure.org/competitions/3/tutoring-outcomes/rules/)) |
| **Manual / Human Intervention during Inference** | Predictions must be automatically generated by container code |

---

### Table 3: ⚠ Allowed with Conditions

| Item | Required Conditions |
| --- | --- |
| **External Datasets** | Must be freely and publicly available to all participants under a permissive commercial open license (CC0, CC-BY, Apache 2.0). |
| **Pretrained LLM / Encoder Weights** | Must have an open commercial license and fit inside `submission.zip` or pre-loaded `huggingface_models/`. |
| **Synthetic / ChatGPT Generated Data** | Generated offline prior to submission and made publicly available under a permissive open license. |
| **Llama Models** | Subject to Meta Llama commercial license terms and organizer approval for open re-licensing. |
| **Winning Solution Licensing** | Must be released under **The MIT License** upon winning. |
| **Top 15 Prize Eligibility** | Final rank requires submitting a PDF Solution Write-Up by Sept 15, 2026. |

---
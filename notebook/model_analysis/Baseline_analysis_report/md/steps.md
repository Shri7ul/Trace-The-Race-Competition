ঠিক আছে। এখন থেকে আমাদের **সব analysis output** যাবে:

```text
notebook/
└── model_analysis/
    ├── baseline model analysis.ipynb
    └── baselineanalysis/
```

আমরা আর analysis-এর output `Trace-The-Race-Dataset/outputs/`-এ রাখব না। Dataset ও existing model artifacts সেখান থেকে শুধু **read** করব; নতুন analysis results থাকবে `baselineanalysis`-এর ভেতরে।

# Final Output Structure

```text
notebook/
└── model_analysis/
    │
    ├── baseline model analysis.ipynb
    │
    └── baselineanalysis/
        │
        ├── 00_setup/
        │   ├── project_paths.json
        │   ├── baseline_manifest.json
        │   ├── environment_info.json
        │   └── artifact_inventory.csv
        │
        ├── 01_baseline_reproduction/
        │   ├── reproduction_metrics.csv
        │   ├── validation_predictions.parquet
        │   ├── model_configuration.json
        │   └── reproduction_report.md
        │
        ├── 02_oof_analysis/
        │   ├── fold_manifest.parquet
        │   ├── word_logistic_oof.parquet
        │   ├── fold_metrics.csv
        │   ├── fold_models/
        │   └── fold_coefficients/
        │
        ├── 03_loss_analysis/
        │   ├── response_error_audit.parquet
        │   ├── error_band_summary.csv
        │   ├── loss_concentration.csv
        │   ├── catastrophic_errors.parquet
        │   ├── false_positive_errors.parquet
        │   ├── false_negative_errors.parquet
        │   └── figures/
        │
        ├── 04_shap_analysis/
        │   ├── global/
        │   ├── local/
        │   ├── error_conditional/
        │   ├── fold_stability/
        │   ├── within_session/
        │   ├── shap_values/
        │   ├── feature_family_summary.csv
        │   └── shortcut_registry.csv
        │
        ├── 05_session_objective_analysis/
        │   ├── session_performance.csv
        │   ├── objective_performance.csv
        │   ├── mixed_label_sessions.parquet
        │   ├── objective_collapse_cases.parquet
        │   └── figures/
        │
        ├── 06_group_analysis/
        │   ├── transcript_length/
        │   ├── objective_frequency/
        │   ├── provider_domain/
        │   ├── transcript_noise/
        │   └── student_tutor_behavior/
        │
        ├── 07_calibration_analysis/
        │   ├── calibration_metrics.csv
        │   ├── confidence_bin_analysis.csv
        │   ├── reliability_data.csv
        │   ├── provider_calibration.csv
        │   └── figures/
        │
        ├── 08_manual_review/
        │   ├── review_sample.parquet
        │   ├── review_template.csv
        │   ├── reviewed_cases.csv
        │   ├── root_cause_taxonomy.csv
        │   └── case_reports/
        │
        ├── 09_counterfactual_analysis/
        │   ├── tutor_masking/
        │   ├── student_removal/
        │   ├── objective_removal/
        │   ├── feedback_removal/
        │   ├── entity_masking/
        │   ├── number_normalization/
        │   └── counterfactual_summary.csv
        │
        ├── 10_ablation_analysis/
        │   ├── objective_only/
        │   ├── transcript_only/
        │   ├── student_only/
        │   ├── tutor_only/
        │   ├── pre_feedback/
        │   ├── final_student_state/
        │   ├── ablation_metrics.csv
        │   └── ablation_comparison.csv
        │
        └── 11_final_research/
            ├── baseline_research_summary.md
            ├── hypothesis_register.csv
            ├── evidence_register.csv
            ├── root_cause_matrix.csv
            ├── upgrade_priority.csv
            └── final_figures/
```

# Analysis Execution Order

আমরা notebook-এ নিচের sequence অনুসরণ করব:

```text
Step 0  → Paths, libraries and output folders
Step 1  → Existing champion baseline শনাক্ত ও reproduce
Step 2  → Five-fold grouped OOF তৈরি
Step 3  → Response-level Log Loss analysis
Step 4  → SHAP ও lexical contribution analysis
Step 5  → Same-session objective discrimination
Step 6  → Group-wise performance analysis
Step 7  → Calibration analysis
Step 8  → Manual error review
Step 9  → Counterfactual sensitivity analysis
Step 10 → Controlled ablation experiments
Step 11 → Final research findings ও V2 recommendation
```

# একমাত্র Model under Analysis

আমাদের primary model হবে:

```text
Model: word_logistic
Input: learning objective + full transcript
Encoding: Word TF-IDF
Classifier: Logistic Regression
```

বর্তমান result:

```text
Validation Log Loss ≈ 0.5455
Validation AUROC    ≈ 0.7036
Public Log Loss     ≈ 0.6163
Public AUROC        ≈ 0.6006
```

`word_char_logistic` analysis-এর primary model হবে না, কারণ tuning-এর পরও সেটি `word_logistic`-কে beat করতে পারেনি। প্রয়োজন হলে comparison model হিসেবে পরে ব্যবহার করব।

# Folder-Creation Rule

Notebook-এর শুরুতেই পুরো directory tree তৈরি হবে। এরপর প্রতিটি section শুধু তার নিজের folder-এ output save করবে।

উদাহরণ:

```text
SHAP output
→ baselineanalysis/04_shap_analysis/

Loss analysis
→ baselineanalysis/03_loss_analysis/

Calibration
→ baselineanalysis/07_calibration_analysis/
```

এতে কোনো CSV, graph, model বা report notebook directory-তে ছড়িয়ে থাকবে না।

# প্রথম কাজ

Analysis-এর প্রথম বাস্তব stage হবে:

> **Step 0: Project Setup, Path Resolution and Baseline Artifact Audit**

এখানে আমরা প্রথমে নিশ্চিত করব:

* Project root সঠিকভাবে পাওয়া যাচ্ছে
* Existing feature-engineering artifacts পাওয়া যাচ্ছে
* `word_logistic` model পাওয়া যাচ্ছে
* Vectorizer পাওয়া যাচ্ছে
* Validation metadata ও labels পাওয়া যাচ্ছে
* Saved predictions এবং reported metrics match করছে
* কোন artifact missing বা inconsistent কি না

এই setup pass করার পরেই OOF এবং SHAP analysis শুরু হবে।

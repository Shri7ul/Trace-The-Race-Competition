# Trace the Ace — Starting Baseline Submission Builder

This starter creates the real code-execution submission ZIP from the model and preprocessing assets already saved in your local project.

## Use

1. Extract this starter folder.
2. Keep `build_submission_package.py` and `runtime_main.py` together.
3. Open a terminal in your Trace the Ace project.
4. Run:

```bash
python /path/to/trace_the_ace_submission_starter/build_submission_package.py
```

The script automatically:

- Finds `Trace-The-Race-Dataset`
- Reads `baseline_results.csv` or `baseline_results_progress.csv`
- Selects the completed non-dummy model with the lowest validation Log Loss
- Retrains a fresh copy on train + validation matrices
- Copies only the assets required by the selected matrix
- Writes `main.py` at the ZIP root
- Creates:

```text
Trace-The-Race-Dataset/
└── outputs/
    └── 06_model_training/
        └── submissions/
            └── submission_starting_baseline.zip
```

Upload `submission_starting_baseline.zip` as a smoke test first.

## Important

The builder must run on the computer containing your real trained models and feature-engineering outputs. The starter ZIP itself does not contain your private model weights or competition data.

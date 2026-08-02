from __future__ import annotations

import json
import platform
import shutil
import zipfile
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy import sparse
from sklearn.base import clone


def find_project_root() -> Path:
    current = Path.cwd().resolve()
    for path in [current, *current.parents]:
        if (path / "Trace-The-Race-Dataset").is_dir():
            return path
    raise FileNotFoundError("Trace-The-Race-Dataset folder was not found.")


def load_matrix(feature_dir: Path, split: str, matrix_key: str):
    if matrix_key == "structured_basic":
        return sparse.load_npz(feature_dir / f"{split}_structured_basic.npz").tocsr()
    if matrix_key == "structured_engineered":
        return sparse.load_npz(feature_dir / f"{split}_structured_engineered.npz").tocsr()
    if matrix_key == "structured_dense":
        return sparse.load_npz(feature_dir / f"{split}_structured_engineered.npz").toarray().astype(np.float32)
    if matrix_key == "word":
        return sparse.load_npz(feature_dir / f"{split}_word_tfidf.npz").tocsr()
    if matrix_key == "char":
        return sparse.load_npz(feature_dir / f"{split}_char_tfidf.npz").tocsr()
    if matrix_key == "word_char":
        word = sparse.load_npz(feature_dir / f"{split}_word_tfidf.npz")
        char = sparse.load_npz(feature_dir / f"{split}_char_tfidf.npz")
        return sparse.hstack([word, char], format="csr")
    if matrix_key == "all_features":
        structured = sparse.load_npz(feature_dir / f"{split}_structured_engineered.npz")
        word = sparse.load_npz(feature_dir / f"{split}_word_tfidf.npz")
        char = sparse.load_npz(feature_dir / f"{split}_char_tfidf.npz")
        return sparse.hstack([structured, word, char], format="csr")
    raise ValueError(f"Unsupported matrix key: {matrix_key}")


def copy_asset(source: Path, asset_dir: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Required asset was not found: {source}")
    shutil.copy2(source, asset_dir / source.name)


def main() -> None:
    project_root = find_project_root()
    dataset_root = project_root / "Trace-The-Race-Dataset"
    feature_dir = dataset_root / "outputs" / "05_feature_engineering"
    model_dir = dataset_root / "outputs" / "06_model_training"
    baseline_model_dir = model_dir / "baseline_models"
    submission_dir = model_dir / "submissions"

    results_file = model_dir / "baseline_results.csv"
    if not results_file.exists():
        results_file = model_dir / "baseline_results_progress.csv"

    results = pd.read_csv(results_file)
    completed = results[
        results["status"].eq("completed")
        & ~results["family"].eq("dummy")
        & results["log_loss"].notna()
    ].sort_values("log_loss").reset_index(drop=True)

    if completed.empty:
        raise ValueError("No completed non-dummy baseline model was found.")

    best = completed.iloc[0]
    model_key = str(best["model_key"])
    matrix_key = str(best["matrix"])
    family = str(best["family"])

    baseline_model_file = baseline_model_dir / f"{model_key}.joblib"
    if not baseline_model_file.exists():
        raise FileNotFoundError(f"Selected baseline model file was not found: {baseline_model_file}")

    X_train = load_matrix(feature_dir, "train", matrix_key)
    X_validation = load_matrix(feature_dir, "validation", matrix_key)
    y_train = np.load(feature_dir / "train_labels.npy")
    y_validation = np.load(feature_dir / "validation_labels.npy")

    if sparse.issparse(X_train):
        X_full = sparse.vstack([X_train, X_validation], format="csr")
    else:
        X_full = np.vstack([X_train, X_validation])

    y_full = np.concatenate([y_train, y_validation])

    model = clone(joblib.load(baseline_model_file))
    model.fit(X_full, y_full)

    package_dir = submission_dir / "starting_baseline_package"
    asset_dir = package_dir / "assets"

    if package_dir.exists():
        shutil.rmtree(package_dir)

    asset_dir.mkdir(parents=True, exist_ok=True)
    submission_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, asset_dir / "model.joblib")

    model_info = {
        "model_key": model_key,
        "family": family,
        "matrix": matrix_key,
        "validation_log_loss": float(best["log_loss"]),
        "full_labelled_rows": int(len(y_full)),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "scipy_version": scipy.__version__,
        "sklearn_version": sklearn.__version__,
    }
    (asset_dir / "model_info.json").write_text(json.dumps(model_info, indent=2), encoding="utf-8")

    source_dir = Path(__file__).resolve().parent
    shutil.copy2(source_dir / "runtime_main.py", package_dir / "main.py")

    if matrix_key == "structured_basic":
        copy_asset(feature_dir / "structured_basic_preprocessor.joblib", asset_dir)
        copy_asset(feature_dir / "band_thresholds.json", asset_dir)

    if matrix_key in {"structured_engineered", "structured_dense", "all_features"}:
        copy_asset(feature_dir / "structured_engineered_preprocessor.joblib", asset_dir)
        copy_asset(feature_dir / "band_thresholds.json", asset_dir)
        copy_asset(feature_dir / "clip_limits.json", asset_dir)

    if matrix_key in {"word", "word_char", "all_features"}:
        copy_asset(feature_dir / "word_tfidf_vectorizer.joblib", asset_dir)

    if matrix_key in {"char", "word_char", "all_features"}:
        copy_asset(feature_dir / "char_tfidf_vectorizer.joblib", asset_dir)

    feature_config = feature_dir / "feature_config.json"
    if feature_config.exists():
        copy_asset(feature_config, asset_dir)

    zip_path = submission_dir / "submission_starting_baseline.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for file_path in sorted(package_dir.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(package_dir).as_posix())

    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()

    if "main.py" not in names:
        raise RuntimeError("Invalid archive: main.py is not at the ZIP root.")

    print("Submission package created successfully.")
    print("Selected model :", model_key)
    print("Matrix         :", matrix_key)
    print("Validation loss:", f"{float(best['log_loss']):.6f}")
    print("ZIP file       :", zip_path)
    print("ZIP size       :", f"{zip_path.stat().st_size / 1024**2:.2f} MB")


if __name__ == "__main__":
    main()

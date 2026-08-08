from __future__ import annotations

import json
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import sparse


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ASSET_DIR = ROOT / "assets"

SHORT_TURN_MAX_WORDS = 5
LONG_TURN_MIN_WORDS = 15

NUMERICAL_FEATURES = [
    "total_turns",
    "total_words",
    "session_duration_minutes",
    "turns_per_minute",
    "student_turns",
    "tutor_turns",
    "student_turn_ratio",
    "student_word_ratio",
    "avg_student_words_per_turn",
    "avg_tutor_words_per_turn",
    "student_short_turn_ratio",
    "student_long_turn_ratio",
    "student_numeric_turn_ratio",
    "student_question_ratio",
    "tutor_question_ratio",
    "student_response_after_tutor_question_ratio",
    "speaker_switch_rate",
    "longest_tutor_streak_ratio",
    "longest_student_streak_ratio",
    "background_turn_ratio",
]


def count_words(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text))


def longest_streak_ratio(roles: list[str], target_role: str) -> float:
    longest = 0
    current = 0
    for role in roles:
        if role == target_role:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest / len(roles) if roles else 0.0


def safe_ratio(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def extract_session_features(session_id: str) -> dict:
    transcript_path = DATA_DIR / "test_transcripts" / f"{session_id}.csv"
    transcript = pd.read_csv(transcript_path)
    transcript.columns = transcript.columns.astype(str).str.replace("\ufeff", "", regex=False).str.strip().str.lower()

    roles = transcript["role"].fillna("").astype(str).str.strip().str.lower()
    contents = transcript["content"].fillna("").astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    word_counts = contents.map(count_words)

    student_mask = roles.eq("student")
    tutor_mask = roles.eq("tutor")
    background_mask = ~(student_mask | tutor_mask)

    total_turns = len(transcript)
    total_words = int(word_counts.sum())
    student_turns = int(student_mask.sum())
    tutor_turns = int(tutor_mask.sum())
    student_words = int(word_counts[student_mask].sum())
    tutor_words = int(word_counts[tutor_mask].sum())

    timestamps = pd.to_datetime(transcript["timestamp"], errors="coerce", utc=True)
    valid_timestamps = timestamps.dropna()
    duration_minutes = 0.0
    if len(valid_timestamps) >= 2:
        duration_minutes = max((valid_timestamps.max() - valid_timestamps.min()).total_seconds() / 60.0, 0.0)

    student_question_turns = int((student_mask & contents.str.contains(r"\?", regex=True)).sum())
    tutor_question_mask = tutor_mask & contents.str.contains(r"\?", regex=True)
    tutor_question_turns = int(tutor_question_mask.sum())

    roles_list = roles.tolist()
    contents_list = contents.tolist()
    student_responses_after_tutor_question = 0
    for index in range(total_turns - 1):
        if roles_list[index] == "tutor" and "?" in contents_list[index] and roles_list[index + 1] == "student":
            student_responses_after_tutor_question += 1

    speaker_switches = sum(roles_list[index] != roles_list[index - 1] for index in range(1, total_turns))
    transcript_text = "\n".join(
        f"[{role.upper()}] {content}"
        for role, content in zip(roles_list, contents_list)
        if content
    )
    student_text = " ".join(contents[student_mask].tolist())
    tutor_text = " ".join(contents[tutor_mask].tolist())

    return {
        "session_id": str(session_id),
        "transcript_text": transcript_text,
        "student_text": student_text,
        "tutor_text": tutor_text,
        "total_turns": total_turns,
        "total_words": total_words,
        "session_duration_minutes": duration_minutes,
        "turns_per_minute": safe_ratio(total_turns, duration_minutes),
        "student_turns": student_turns,
        "tutor_turns": tutor_turns,
        "student_turn_ratio": safe_ratio(student_turns, total_turns),
        "student_word_ratio": safe_ratio(student_words, total_words),
        "avg_student_words_per_turn": safe_ratio(student_words, student_turns),
        "avg_tutor_words_per_turn": safe_ratio(tutor_words, tutor_turns),
        "student_short_turn_ratio": float((word_counts[student_mask] <= SHORT_TURN_MAX_WORDS).mean()) if student_turns else 0.0,
        "student_long_turn_ratio": float((word_counts[student_mask] >= LONG_TURN_MIN_WORDS).mean()) if student_turns else 0.0,
        "student_numeric_turn_ratio": float(contents[student_mask].str.contains(r"\d", regex=True).mean()) if student_turns else 0.0,
        "student_question_ratio": safe_ratio(student_question_turns, student_turns),
        "tutor_question_ratio": safe_ratio(tutor_question_turns, tutor_turns),
        "student_response_after_tutor_question_ratio": safe_ratio(student_responses_after_tutor_question, tutor_question_turns),
        "speaker_switch_rate": safe_ratio(speaker_switches, total_turns - 1),
        "longest_tutor_streak_ratio": longest_streak_ratio(roles_list, "tutor"),
        "longest_student_streak_ratio": longest_streak_ratio(roles_list, "student"),
        "background_turn_ratio": float(background_mask.mean()) if total_turns else 0.0,
    }


def apply_saved_bands(data: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    data = data.copy()
    for band_column, settings in thresholds.items():
        source = settings["source_feature"]
        values = pd.to_numeric(data[source], errors="coerce").fillna(settings["fill_value"])
        labels = np.select(
            [
                values <= settings["low_upper_threshold"],
                values <= settings["medium_upper_threshold"],
            ],
            ["LOW", "MEDIUM"],
            default="HIGH",
        )
        data[band_column] = pd.Series(labels, index=data.index, dtype="string")
    return data


def build_basic_structured(data: pd.DataFrame):
    preprocessor = joblib.load(ASSET_DIR / "structured_basic_preprocessor.joblib")
    thresholds = json.loads((ASSET_DIR / "band_thresholds.json").read_text(encoding="utf-8"))
    data = apply_saved_bands(data, thresholds)
    numeric = preprocessor["imputer"].transform(data[preprocessor["numerical_features"]])
    numeric = preprocessor["scaler"].transform(numeric).astype(np.float32)
    bands = preprocessor["band_encoder"].transform(data[preprocessor["band_features"]])
    return sparse.hstack([sparse.csr_matrix(numeric), bands], format="csr")


def build_engineered_structured(data: pd.DataFrame):
    preprocessor = joblib.load(ASSET_DIR / "structured_engineered_preprocessor.joblib")
    thresholds = json.loads((ASSET_DIR / "band_thresholds.json").read_text(encoding="utf-8"))
    clip_limits = json.loads((ASSET_DIR / "clip_limits.json").read_text(encoding="utf-8"))
    data = apply_saved_bands(data, thresholds)

    clipped = pd.DataFrame(index=data.index)
    for column, limits in clip_limits.items():
        values = pd.to_numeric(data[column], errors="coerce")
        clipped[column] = values.clip(lower=limits["lower"], upper=limits["upper"])

    for source_column in preprocessor["log_source_features"]:
        clipped[f"log_{source_column}"] = np.log1p(clipped[source_column].clip(lower=0))

    numeric_columns = preprocessor["numerical_features"]
    numeric = preprocessor["imputer"].transform(clipped[numeric_columns])
    numeric = preprocessor["scaler"].transform(numeric).astype(np.float32)
    bands = preprocessor["band_encoder"].transform(data[preprocessor["band_features"]])
    return sparse.hstack([sparse.csr_matrix(numeric), bands], format="csr")


def build_model_matrix(data: pd.DataFrame, matrix_key: str):
    text = data["model_text"].fillna("").astype(str)

    if matrix_key == "structured_basic":
        return build_basic_structured(data)
    if matrix_key == "structured_engineered":
        return build_engineered_structured(data)
    if matrix_key == "structured_dense":
        return build_engineered_structured(data).toarray().astype(np.float32)
    if matrix_key == "word":
        vectorizer = joblib.load(ASSET_DIR / "word_tfidf_vectorizer.joblib")
        return vectorizer.transform(text).tocsr()
    if matrix_key == "char":
        vectorizer = joblib.load(ASSET_DIR / "char_tfidf_vectorizer.joblib")
        return vectorizer.transform(text).tocsr()
    if matrix_key == "word_char":
        word_vectorizer = joblib.load(ASSET_DIR / "word_tfidf_vectorizer.joblib")
        char_vectorizer = joblib.load(ASSET_DIR / "char_tfidf_vectorizer.joblib")
        return sparse.hstack([word_vectorizer.transform(text), char_vectorizer.transform(text)], format="csr")
    if matrix_key == "all_features":
        structured = build_engineered_structured(data)
        word_vectorizer = joblib.load(ASSET_DIR / "word_tfidf_vectorizer.joblib")
        char_vectorizer = joblib.load(ASSET_DIR / "char_tfidf_vectorizer.joblib")
        return sparse.hstack(
            [structured, word_vectorizer.transform(text), char_vectorizer.transform(text)],
            format="csr",
        )
    raise ValueError(f"Unsupported matrix key: {matrix_key}")


def main() -> None:
    model_info = json.loads((ASSET_DIR / "model_info.json").read_text(encoding="utf-8"))
    model = joblib.load(ASSET_DIR / "model.joblib")

    test_features = pd.read_csv(DATA_DIR / "test_features.csv")
    test_features.columns = test_features.columns.astype(str).str.replace("\ufeff", "", regex=False).str.strip().str.lower()
    test_features["response_id"] = test_features["response_id"].astype("string").str.strip()
    test_features["session_id"] = test_features["session_id"].astype("string").str.strip()
    test_features["learning_objective"] = test_features["learning_objective"].fillna("").astype("string").str.replace(r"\s+", " ", regex=True).str.strip()

    session_rows = [
        extract_session_features(session_id)
        for session_id in test_features["session_id"].drop_duplicates().tolist()
    ]
    session_features = pd.DataFrame(session_rows)
    model_data = test_features.merge(session_features, on="session_id", how="left", validate="many_to_one")

    for column in NUMERICAL_FEATURES:
        model_data[column] = pd.to_numeric(model_data[column], errors="coerce").replace([np.inf, -np.inf], np.nan)
    for column in ["transcript_text", "student_text", "tutor_text"]:
        model_data[column] = model_data[column].fillna("").astype("string").str.replace(r"\s+", " ", regex=True).str.strip()

    model_data["model_text"] = (
        "[OBJECTIVE] " + model_data["learning_objective"]
        + "\n[TRANSCRIPT] " + model_data["transcript_text"]
    )

    matrix = build_model_matrix(model_data, model_info["matrix"])
    probabilities = np.clip(model.predict_proba(matrix)[:, 1], 1e-6, 1 - 1e-6)

    predictions = pd.DataFrame({"response_id": model_data["response_id"], "probability": probabilities})
    submission_format = pd.read_csv(DATA_DIR / "submission_format.csv")
    submission_format.columns = submission_format.columns.astype(str).str.replace("\ufeff", "", regex=False).str.strip().str.lower()
    submission_format["response_id"] = submission_format["response_id"].astype("string").str.strip()

    submission = submission_format[["response_id"]].merge(
        predictions,
        on="response_id",
        how="left",
        validate="one_to_one",
    )

    if submission["probability"].isna().any():
        raise ValueError("Missing predictions found in submission output.")

    submission.to_csv(ROOT / "submission.csv", index=False)


if __name__ == "__main__":
    main()

"""Execute the v2 notebook cell against the completed baseline artifact."""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path

import pandas as pd


notebook = json.loads(Path("feature.ipynb").read_text(encoding="utf-8"))
namespace: dict[str, object] = {}

# Setup and transcript parser definitions used by the appended v2 cell.
for cell_index in (2, 17):
    source = "".join(notebook["cells"][cell_index]["source"])
    exec(compile(source, f"feature.ipynb:cell-{cell_index}", "exec"), namespace)

# Reuse the completed baseline artifact rather than rerunning exploratory plots and exports.
engineered_df = pd.read_parquet("train_engineered.parquet")
sample_rows = int(os.getenv("V2_SAMPLE_ROWS", "0"))
if sample_rows:
    engineered_df = engineered_df.head(sample_rows).copy()
namespace["engineered_df"] = engineered_df
namespace["df"] = engineered_df

# Extract only the literal description catalog from the baseline export cell.
catalog_source = "".join(notebook["cells"][38]["source"])
catalog_tree = ast.parse(catalog_source)
catalog_assignment = next(
    node
    for node in catalog_tree.body
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "FEATURE_DESCRIPTIONS" for target in node.targets)
)
exec(compile(ast.Module(body=[catalog_assignment], type_ignores=[]), "feature.ipynb:catalog", "exec"), namespace)

v2_source = "".join(notebook["cells"][-1]["source"])
exec(compile(v2_source, "feature.ipynb:v2", "exec"), namespace)

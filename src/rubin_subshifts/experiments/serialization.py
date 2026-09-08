"""JSON, CSV, and ZIP serialization for experiment results."""

from __future__ import annotations

import io
import json
import zipfile

import pandas as pd

from rubin_subshifts.experiments.models import ExperimentResult


def result_json(result: ExperimentResult) -> bytes:
    """Serialize an experiment result as indented UTF-8 JSON."""
    value = {
        "identifier": result.identifier,
        "status": result.status.value,
        "summary": result.summary,
        "guarantee": result.guarantee.value,
        "payload": result.payload,
        "error": result.error,
    }
    return json.dumps(value, indent=2, sort_keys=True).encode()


def feature_table_csv(result: ExperimentResult, side: str = "left") -> bytes:
    """Serialize signature feature vectors as a tidy CSV table."""
    signature = result.payload[side]
    periods = signature["periods"]
    rows: list[dict[str, object]] = []
    for name, values in signature["features"]:
        rows.extend(
            {"system": signature["system_name"], "feature": name, "period": period, "value": value}
            for period, value in zip(periods, values, strict=True)
        )
    return str(pd.DataFrame(rows).to_csv(index=False)).encode()


def result_bundle(result: ExperimentResult) -> bytes:
    """Create an in-memory reproducibility ZIP bundle."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("experiment.json", result_json(result))
        archive.writestr(
            "summary.md",
            f"# Experiment {result.identifier}\n\n{result.summary}\n\n"
            f"Guarantee: `{result.guarantee.value}`\n",
        )
        if result.payload:
            archive.writestr("tables/left-features.csv", feature_table_csv(result, "left"))
            archive.writestr("tables/right-features.csv", feature_table_csv(result, "right"))
    return buffer.getvalue()

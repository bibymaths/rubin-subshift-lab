"""Service-layer experiment execution independent of Streamlit."""

from __future__ import annotations

from rubin_subshifts.config import AlgorithmicGuarantee, ExperimentStatus
from rubin_subshifts.experiments.models import ExperimentConfig, ExperimentResult
from rubin_subshifts.reconstruction.experiments import compare_signatures
from rubin_subshifts.reconstruction.signatures import build_signature
from rubin_subshifts.symbolic.sft import OneStepSFT
from rubin_subshifts.symbolic.subshifts import FiniteSubshift, binary_full_shift


def run_signature_comparison(config: ExperimentConfig) -> ExperimentResult:
    """Run the built-in full-shift versus golden-mean comparison."""
    examples: dict[str, FiniteSubshift] = {
        "binary_full_shift": binary_full_shift(),
        "golden_mean_shift": OneStepSFT.golden_mean(),
    }
    try:
        left = examples[config.left_example]
        right = examples[config.right_example]
    except KeyError as exc:
        return ExperimentResult(
            config.identifier,
            ExperimentStatus.FAILED,
            "unknown built-in example",
            AlgorithmicGuarantee.EXPERIMENTAL,
            {},
            str(exc),
        )
    left_signature = build_signature(
        left,
        config.periods,
        random_seed=config.random_seed,
        max_configurations=config.limits.max_configurations,
    )
    right_signature = build_signature(
        right,
        config.periods,
        random_seed=config.random_seed,
        max_configurations=config.limits.max_configurations,
    )
    comparison = compare_signatures(left_signature, right_signature)
    status = (
        ExperimentStatus.TRUNCATED
        if left_signature.truncated or right_signature.truncated
        else ExperimentStatus.COMPLETED
    )
    return ExperimentResult(
        config.identifier,
        status,
        comparison.statement,
        comparison.guarantee,
        {
            "config": config.model_dump(mode="json"),
            "left": left_signature.to_json(),
            "right": right_signature.to_json(),
            "comparison": {
                "matching_features": comparison.matching_features,
                "differing_features": comparison.differing_features,
                "statement": comparison.statement,
            },
        },
    )

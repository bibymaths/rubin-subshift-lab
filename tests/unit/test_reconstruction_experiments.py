"""Finite reconstruction, experiment, and serialization tests."""

from __future__ import annotations

import json
import zipfile
from io import BytesIO

import numpy as np
import pytest
from pydantic import ValidationError

from rubin_subshifts.config import AlgorithmicGuarantee, ComputationLimits, ExperimentStatus
from rubin_subshifts.exceptions import DomainValidationError
from rubin_subshifts.experiments.models import ExperimentConfig
from rubin_subshifts.experiments.runner import run_signature_comparison
from rubin_subshifts.experiments.serialization import feature_table_csv, result_bundle, result_json
from rubin_subshifts.groups.permutations import Permutation
from rubin_subshifts.reconstruction.cylinder_proxies import CylinderProxy
from rubin_subshifts.reconstruction.experiments import compare_signatures
from rubin_subshifts.reconstruction.incidence import fixed_point_incidence
from rubin_subshifts.reconstruction.signatures import build_signature
from rubin_subshifts.symbolic import Alphabet, Word
from rubin_subshifts.symbolic.sft import OneStepSFT
from rubin_subshifts.symbolic.subshifts import binary_full_shift, golden_mean_shift


def test_signature_metadata_counts_and_feature_access() -> None:
    periods = (1, 2, 3, 4, 5, 6)
    signature = build_signature(
        OneStepSFT.golden_mean(),
        periods,
        generators=("shift",),
        random_seed=17,
        timestamp="2026-01-01T00:00:00+00:00",
    )
    assert signature.feature("periodic_point_count") == (1.0, 3.0, 4.0, 7.0, 11.0, 18.0)
    assert signature.feature("least_period_count") == (1.0, 2.0, 3.0, 4.0, 10.0, 12.0)
    assert signature.guarantee is AlgorithmicGuarantee.EXACT_FINITE
    assert signature.completed and not signature.truncated
    assert signature.generators == ("shift",)
    assert signature.created_at == "2026-01-01T00:00:00+00:00"
    assert signature.to_json()["guarantee"] == "exact_finite"
    with pytest.raises(DomainValidationError, match="no feature"):
        signature.feature("missing")
    with pytest.raises(DomainValidationError, match="positive"):
        build_signature(binary_full_shift(), ())


def test_forbidden_signature_truncates_without_materialization() -> None:
    signature = build_signature(golden_mean_shift(), (1, 10), max_configurations=100)
    assert signature.truncated
    assert not signature.completed
    assert signature.feature("periodic_point_count") == (1.0, -1.0)
    assert signature.feature("least_period_count") == (1.0, -1.0)


def test_signature_comparison_and_period_validation() -> None:
    left = build_signature(binary_full_shift(), (1, 2, 3), timestamp="x")
    right = build_signature(OneStepSFT.golden_mean(), (1, 2, 3), timestamp="x")
    comparison = compare_signatures(left, right)
    assert comparison.distinguished_within_bounds
    assert comparison.statement == "distinguished by the selected finite invariants"
    assert comparison.differing_features == ("least_period_count", "periodic_point_count")
    identical = compare_signatures(left, left)
    assert not identical.distinguished_within_bounds
    assert identical.matching_features == ("least_period_count", "periodic_point_count")
    with pytest.raises(DomainValidationError, match="identical period"):
        compare_signatures(left, build_signature(binary_full_shift(), (1, 2)))


def test_cylinder_and_incidence(binary: Alphabet) -> None:
    proxy = CylinderProxy(Word(binary, (0, 1)), offset=1)
    assert proxy.contains(Word(binary, (1, 0, 1, 1)))
    assert not proxy.contains(Word(binary, (0, 0)))
    assert not CylinderProxy(Word(binary, (0,)), offset=-1).contains(Word(binary, (0,)))
    elements = (Permutation.identity(3), Permutation((1, 0, 2)))
    incidence = fixed_point_incidence(elements)
    assert incidence.dtype == np.bool_
    assert incidence.tolist() == [[True, True, True], [False, False, True]]
    assert fixed_point_incidence(()).shape == (0, 0)


def test_computation_limits_and_config_identifier() -> None:
    limits = ComputationLimits(max_period=12)
    assert limits.state_space_size(2, 12) == 4096
    assert limits.rule_space_size(2, 3) == 256
    config = ExperimentConfig(periods=(1, 2, 3), random_seed=4, limits=limits)
    assert (
        config.identifier
        == ExperimentConfig(periods=(1, 2, 3), random_seed=4, limits=limits).identifier
    )
    with pytest.raises(ValidationError, match="positive"):
        ExperimentConfig(periods=(0,))
    with pytest.raises(ValidationError, match="unique and increasing"):
        ExperimentConfig(periods=(2, 1))


def test_experiment_runner_success_failure_and_exports() -> None:
    config = ExperimentConfig(periods=(1, 2, 3, 4))
    result = run_signature_comparison(config)
    assert result.status is ExperimentStatus.COMPLETED
    assert result.guarantee is AlgorithmicGuarantee.EXPERIMENTAL
    decoded = json.loads(result_json(result))
    assert decoded["identifier"] == config.identifier
    assert decoded["status"] == "completed"
    csv_data = feature_table_csv(result).decode()
    assert "periodic_point_count" in csv_data
    bundle = result_bundle(result)
    with zipfile.ZipFile(BytesIO(bundle)) as archive:
        assert set(archive.namelist()) == {
            "experiment.json",
            "summary.md",
            "tables/left-features.csv",
            "tables/right-features.csv",
        }
    bad = run_signature_comparison(
        ExperimentConfig(left_example="unknown", right_example="golden_mean_shift")
    )
    assert bad.status is ExperimentStatus.FAILED
    assert bad.error is not None
    assert json.loads(result_json(bad))["payload"] == {}
    with zipfile.ZipFile(BytesIO(result_bundle(bad))) as archive:
        assert set(archive.namelist()) == {"experiment.json", "summary.md"}

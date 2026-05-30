"""Pareto domination unit tests."""

from __future__ import annotations

import pytest

from agentdex.modules.battles.result import Domination
from agentdex.modules.evolver.pareto import dominates

OBJECTIVES = {"accuracy": "maximize", "cost": "minimize", "latency_s": "minimize"}


def test_a_clearly_dominates() -> None:
    a = {"accuracy": 1.0, "cost": 0.5, "latency_s": 0.1}
    b = {"accuracy": 0.5, "cost": 1.0, "latency_s": 0.5}
    assert dominates(a, b, OBJECTIVES) == Domination.A_DOMINATES


def test_b_clearly_dominates() -> None:
    a = {"accuracy": 0.0, "cost": 5.0, "latency_s": 5.0}
    b = {"accuracy": 1.0, "cost": 1.0, "latency_s": 0.1}
    assert dominates(a, b, OBJECTIVES) == Domination.B_DOMINATES


def test_tie_identical_scores() -> None:
    a = {"accuracy": 0.7, "cost": 1.0, "latency_s": 0.2}
    b = {"accuracy": 0.7, "cost": 1.0, "latency_s": 0.2}
    assert dominates(a, b, OBJECTIVES) == Domination.TIE


def test_tie_mixed_better_and_worse() -> None:
    # A better at accuracy, worse at cost → neither dominates
    a = {"accuracy": 1.0, "cost": 2.0, "latency_s": 0.5}
    b = {"accuracy": 0.5, "cost": 1.0, "latency_s": 0.5}
    assert dominates(a, b, OBJECTIVES) == Domination.TIE


def test_missing_objective_raises() -> None:
    a = {"accuracy": 1.0}
    b = {"accuracy": 0.5}
    with pytest.raises(ValueError, match="cost"):
        dominates(a, b, OBJECTIVES)


def test_unknown_direction_raises() -> None:
    a = {"x": 1.0}
    b = {"x": 0.5}
    with pytest.raises(ValueError, match="direction"):
        dominates(a, b, {"x": "wiggle"})

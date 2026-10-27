"""Experiment-portfolio simulator and decision rules (ECON 5200 PS2)."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

def simulate_portfolio(n: int, seed: int, **kwargs):
    """Return the experiment log with the true effect attached."""
    rng = np.random.default_rng(seed)

    with_effect = rng.random(n) >= 0.80
    true_effect = np.zeros(n)
    true_effect[with_effect] = rng.uniform(500, 1500, with_effect.sum())

    sample_size = rng.integers(50, 5001, n)
    standard_error = 15000 * np.sqrt(2 / sample_size)
    estimated_effect = true_effect + rng.normal(0, standard_error)

    z = estimated_effect / standard_error
    p_value = 2 * stats.norm.sf(abs(z))

    log = pd.DataFrame({
        "experiment": np.arange(1, n + 1),
        "true_effect": true_effect,
        "n_per_group": sample_size,
        "standard_error": standard_error,
        "estimated_effect": estimated_effect,
        "p_value": p_value
    })

    return log


def apply_rule(log, rule):
    """Ship decisions under `rule`: the p < 0.05 threshold and at least one other."""
    if rule == "client":
        return log["p_value"] < 0.05
    elif rule == "proposed":
        return (log["p_value"] < 0.01) & (log["estimated_effect"] > 0)
    else:
        raise ValueError("Use client or proposed.")


def evaluate(log, rule):
    """Realised true return, ship count and false-ship rate under `rule`."""
    shipped = log[apply_rule(log, rule)]

    return {
        "realised_return": shipped["true_effect"].sum(),
        "ship_count": len(shipped),
        "false_ship_rate": (shipped["true_effect"] == 0).mean()
    }


if __name__ == "__main__":
    ...   # demonstration plus at least three assertions that must hold
    demo = simulate_portfolio(20, 99)
    print("Client:", evaluate(demo, "client"))
    print("Proposed:", evaluate(demo, "proposed"))

    # Check an example where we know the answers
    example = pd.DataFrame({
        "p_value": [0.001, 0.03, 0.50],
        "estimated_effect": [1200, 200, 100],
        "true_effect": [1000, 0, 0]
    })

    result = evaluate(example, "client")
    assert result["realised_return"] == 1000
    assert result["ship_count"] == 2
    assert result["false_ship_rate"] == 0.5

    print("All checks passed.")

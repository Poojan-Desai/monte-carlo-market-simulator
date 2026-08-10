import numpy as np
import pytest

from market_simulator import simulate_paths, summarize


def test_simulation_is_reproducible_and_keeps_starting_price() -> None:
    returns = np.array([-0.02, 0.01, 0.03])
    first = simulate_paths(100, returns, days=5, simulations=10, seed=7)
    second = simulate_paths(100, returns, days=5, simulations=10, seed=7)

    np.testing.assert_array_equal(first, second)
    np.testing.assert_array_equal(first[:, 0], np.full(10, 100))
    assert first.shape == (10, 6)


def test_summary_uses_terminal_distribution() -> None:
    paths = np.array([[100, 90], [100, 100], [100, 110]], dtype=float)
    result = summarize(paths)

    assert result["simulations"] == 3
    assert result["days"] == 1
    assert result["median_terminal_price"] == 100


def test_simulation_rejects_empty_returns() -> None:
    with pytest.raises(ValueError, match="finite historical return"):
        simulate_paths(100, np.array([]), days=5, simulations=10, seed=7)

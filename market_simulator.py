"""Bootstrap historical returns into reproducible market-price scenarios."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf


def fetch_history(ticker: str, period: str) -> pd.Series:
    """Download adjusted closing prices and validate the response."""
    history = yf.Ticker(ticker).history(period=period, auto_adjust=True)
    if history.empty or "Close" not in history:
        raise ValueError(f"No closing-price history returned for {ticker!r}")
    closes = history["Close"].dropna().astype(float)
    if len(closes) < 3:
        raise ValueError("At least three closing prices are required")
    return closes


def simulate_paths(
    last_price: float,
    historical_returns: np.ndarray,
    days: int,
    simulations: int,
    seed: int,
) -> np.ndarray:
    """Sample daily historical returns with replacement and compound each path."""
    if last_price <= 0 or days < 1 or simulations < 1:
        raise ValueError("Price, days, and simulation count must be positive")
    returns = np.asarray(historical_returns, dtype=float)
    returns = returns[np.isfinite(returns)]
    if returns.size == 0:
        raise ValueError("At least one finite historical return is required")

    generator = np.random.default_rng(seed)
    sampled_returns = generator.choice(returns, size=(simulations, days), replace=True)
    growth = np.cumprod(1 + sampled_returns, axis=1)
    start = np.full((simulations, 1), last_price)
    return np.concatenate([start, last_price * growth], axis=1)


def summarize(paths: np.ndarray) -> dict[str, float | int]:
    """Summarize the distribution of ending scenario prices."""
    terminal_prices = paths[:, -1]
    return {
        "simulations": int(paths.shape[0]),
        "days": int(paths.shape[1] - 1),
        "mean_terminal_price": float(np.mean(terminal_prices)),
        "median_terminal_price": float(np.median(terminal_prices)),
        "p05_terminal_price": float(np.percentile(terminal_prices, 5)),
        "p95_terminal_price": float(np.percentile(terminal_prices, 95)),
    }


def save_charts(ticker: str, closes: pd.Series, paths: np.ndarray, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    figure, axis = plt.subplots(figsize=(10, 6))
    axis.plot(closes.index, closes.values, label="Adjusted close")
    axis.set(title=f"{ticker} historical adjusted close", xlabel="Date", ylabel="USD")
    axis.grid(alpha=0.3)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_dir / "history.png", dpi=160)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(10, 6))
    for path in paths[: min(250, len(paths))]:
        axis.plot(path, alpha=0.08, color="#2563eb")
    axis.set(
        title=f"{ticker} bootstrapped price scenarios",
        xlabel="Trading days",
        ylabel="USD",
    )
    axis.grid(alpha=0.3)
    figure.tight_layout()
    figure.savefig(output_dir / "scenarios.png", dpi=160)
    plt.close(figure)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker", nargs="?", default="AAPL")
    parser.add_argument("--period", default="1y")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--simulations", type=int, default=1_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    closes = fetch_history(args.ticker.upper(), args.period)
    returns = closes.pct_change().dropna().to_numpy()
    paths = simulate_paths(
        float(closes.iloc[-1]), returns, args.days, args.simulations, args.seed
    )
    results = summarize(paths)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    save_charts(args.ticker.upper(), closes, paths, args.output)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

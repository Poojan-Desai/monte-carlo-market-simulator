# Monte Carlo Market Scenario Simulator

A small Python data project that resamples historical daily returns to produce a
distribution of possible future price paths. It reports terminal-price
percentiles, return ranges, the simulated chance of finishing below the start,
and the mean outcome in the worst 5% tail, then saves reproducible charts.

This is a **scenario-analysis exercise, not a stock-price prediction system**.
Bootstrap simulations assume the sampled historical returns are informative
about a future window and do not model regime changes, news, liquidity, or
transaction costs. The output is not investment advice.

## Method

1. Download adjusted closing prices with `yfinance`.
2. Calculate historical daily percentage returns.
3. Sample those returns with replacement using a fixed random seed.
4. Compound each sampled series from the latest observed price.
5. Report price percentiles plus explicit return and downside-tail indicators.

The bootstrap preserves the empirical one-day return distribution, but it does
not preserve serial dependence or prove that the distribution will remain
stable.

The downside fields are descriptive properties of the simulated paths—not
validated Value-at-Risk estimates and not forecasts of real losses.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python market_simulator.py AAPL --period 1y --days 30 --simulations 1000 --seed 42
```

Results are written to `artifacts/summary.json`, `artifacts/history.png`, and
`artifacts/scenarios.png`. Market data requires an internet connection and is
provided by Yahoo Finance through `yfinance`.

## Test

```bash
pip install -r requirements-dev.txt
pytest
```

Tests exercise deterministic simulation, downside calculations, and malformed
input handling without making a network request.

## Stack

Python, NumPy, pandas, Matplotlib, yfinance, and pytest.

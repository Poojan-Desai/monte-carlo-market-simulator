import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

# Specify the stock ticker symbol
ticker = "AAPL"

# Fetch historical data for the past year
stock = yf.Ticker(ticker)
data = stock.history(period="1y")

# Plot the closing price
plt.figure(figsize=(10, 6))
plt.plot(data['Close'], label="Closing Price")
plt.title(f"{ticker} Closing Prices")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid()
plt.show()

# Monte Carlo Simulation
last_price = data['Close'][-1]
returns = data['Close'].pct_change().dropna()
num_simulations = 1000
days_to_simulate = 30
simulated_prices = []
for _ in range(num_simulations):
    prices = [last_price]
    for _ in range(days_to_simulate):
        next_price = prices[-1] * (1 + np.random.choice(returns))
        prices.append(next_price)
    simulated_prices.append(prices)

# Plot simulation results
plt.figure(figsize=(10, 6))
for simulation in simulated_prices:
    plt.plot(simulation, alpha=0.1, color='blue')
plt.title(f"{ticker} Monte Carlo Simulation - {num_simulations} Runs")
plt.xlabel("Days")
plt.ylabel("Price (USD)")
plt.grid()
plt.show()

# Analyze simulations
final_prices = [prices[-1] for prices in simulated_prices]
mean_price = np.mean(final_prices)
median_price = np.median(final_prices)
percentile_5 = np.percentile(final_prices, 5)
percentile_95 = np.percentile(final_prices, 95)

# Print results
print(f"Monte Carlo Simulation Results for {ticker}:")
print(f"Mean price after {days_to_simulate} days: ${mean_price:.2f}")
print(f"Median price after {days_to_simulate} days: ${median_price:.2f}")
print(f"5th percentile (pessimistic): ${percentile_5:.2f}")
print(f"95th percentile (optimistic): ${percentile_95:.2f}")

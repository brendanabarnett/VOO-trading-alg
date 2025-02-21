# VOO Trading Algorithm: Outperforming the S&P 500

## Goal
- **Outpreform the S&P 500 by strategically buying/selling VOO (S&P ETF)**

## Description
This program aims to outperform the S&P 500 index by strategically buying and selling shares of VOO, an ETF that tracks the S&P 500. The strategy uses technical indicators to make informed decisions on when to enter and exit positions. Essentially, we aim to beat the S&P by using the S&P.

## Assumptions
- When not invested in VOO, the cash balance does not earn any interest (0% interest rate)
- All buy/sell transactions are executed at market close

## Dependencies
- `yfinance`
- `numpy`
- `pandas`
- `plotly`
- `ta`

## Technical Indicators Used
- Bollinger Bands
- MACD (Moving Average Convergence Divergence)
- RSI (Relative Strength Index)
- SMA (Simple Moving Average)

## Simulation Setup
- Initial Investment: $10,000
- Trading Days per Year: 252
- Ticker: VOO (S&P 500 ETF)
- Evaluation Periods: 0.5, 1, 2, and 3 years

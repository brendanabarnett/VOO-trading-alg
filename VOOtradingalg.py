# Goal:
#     - Beating the S&P 500 by Optimally Buying/Selling VOO
#
# Description:
#     - This program aims to outperform the S&P 500 index by strategically buying and selling
#     shares of VOO, an ETF that tracks the S&P 500
#     - The strategy is based on technical indicators to make informed decisions on when to enter and exit positions
#
# Assumptions:
#     - When not invested in VOO, the cash balance does not earn any interest (0% interest rate)
#     - Always buy/sell at close

"""# Dependencies"""

import yfinance as yf
import numpy as np
import pandas as pd
import time
import datetime
import plotly.express as px
import ta     # technical analysis library

"""# Statistical Methods"""

def percent_change(initial, final):
    return ((final - initial) / initial) * 100

def percent_difference(value1, value2):
    return (value1 - value2) / ((value1 + value2) / 2) * 100

def average(arr):
    return sum(arr) / len(arr) if arr else 0

def BollingerBands(data):
  indicator_bb = ta.volatility.BollingerBands(close=data["Close"], window=21, window_dev=2)

  data['bb_mavg'] = indicator_bb.bollinger_mavg()
  data['bb_Hband'] = indicator_bb.bollinger_hband()
  data['bb_Lband'] = indicator_bb.bollinger_lband()
  data['bb_Hind'] = indicator_bb.bollinger_hband_indicator()    # high indicator
  data['bb_Lind'] = indicator_bb.bollinger_lband_indicator()    # low indicator
  data['bb_w'] = indicator_bb.bollinger_wband()                 # width size bb
  data['bb_p'] = indicator_bb.bollinger_pband()                 # % bb

def MACD(data):
  indicator_mac = ta.trend.MACD(close=data["Close"], window_slow= 26, window_fast= 12, window_sign= 9, fillna = False)

  data['mac'] = indicator_mac.macd()
  data['mac_dif'] = indicator_mac.macd_diff()
  data['mac_ind'] = indicator_mac.macd_signal()

def RSI(data):
  indicator_rsi = ta.momentum.RSIIndicator(close=data["Close"], window = 21, fillna = False)
  indicator_rsi1 = ta.momentum.RSIIndicator(close=data["Close"], window = 100, fillna = False)

  data["rsi"] = indicator_rsi.rsi()
  data['rsi_l'] = indicator_rsi1.rsi()

def SMA(data):
  indicator_sma_l = ta.trend.SMAIndicator(close=data["Close"], window= 200, fillna = False)
  indicator_sma_s = ta.trend.SMAIndicator(close=data["Close"], window= 50, fillna = False)
  indicator_sma_ll = ta.trend.SMAIndicator(close=data["Close"], window= 500, fillna = False)

  data["sma_200"] = indicator_sma_l.sma_indicator()
  data["sma_50"] = indicator_sma_s.sma_indicator()
  data["sma_500"] = indicator_sma_ll.sma_indicator()

"""# Simulation Helpers"""

def Performance(results):
  '''Displaying the results'''

  print()
  diffs = list()
  for key, value in results.items():
    key = key.split()

    if "Optimized" in key:
      print(f"Optimized {key[1]} yrs: ${value[0]:.2f}, percentChange: {percent_change(INITIAL_INVESTMENT, value[0]):.2f}%, transactions: {value[1]}")
      dif = percent_difference(value[0], results[f'Baseline {key[1]}'])
      diffs.append(dif)
      print(f"Percent Difference: {dif:.2f}%")
      print()

    else:
      print(f"Baseline {key[1]} yrs: ${value:.2f}, percentChange: {percent_change(INITIAL_INVESTMENT, value):.2f}%")

  return diffs

def Sell(day, data):
  '''Returns True if we should sell VOO on the given day'''

  if (data['rsi'][day] > 70 or data['rsi_l'][day] > 60):  # overbought
    return True

  if (data['sma_50'][day] > data['sma_200'][day]):       # positive deviation from long term
    if (data['Close'][day] < data['bb_Lband'][day]):      # look to position of close
      return True

  elif (data['sma_50'][day] < data['sma_200'][day]):      # negative deviation from long term
    if (data['sma_200'][day] < data['bb_Hband'][day]):      # look to long term avg
      return True

  return False

def Buy(day, data):
  '''Returns True if we should buy VOO on the given day'''

  if (data['rsi'][day] > 70 or data['rsi_l'][day] > 60):    # overbought
    return False

  if (data['sma_50'][day] > data['sma_200'][day]):       # positive deviation from long term
    if (data['Close'][day] > data['bb_Lband'][day]):      # look to position of close
      return True

  elif (data['sma_50'][day] < data['sma_200'][day]):     # negative deviation from long term
    if(data['bb_Hband'][day] < data['sma_50'][day]):      # look to mid term avg
      return True

  return False

"""# Simulation Setup & Function"""

TRADING_DAYS_PER_YEAR = 252
DAYS_IN_PAST = 20000
INITIAL_INVESTMENT = 10000.0    # $10,000
TICKER = 'VOO' # s&p 500
YEARS = [.5, 1, 2, 3]
RESULTS = dict()

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=DAYS_IN_PAST)

data = yf.download(TICKER, start=start_date, end=end_date)
data['Date'] = data.index

def MainSimulation(data):
  '''Man sim'''

  # adding columns to data
  BollingerBands(data)
  MACD(data)
  RSI(data)
  SMA(data)

  for years_ago in YEARS:

    start = int (len(data)-years_ago*TRADING_DAYS_PER_YEAR)
    print(years_ago, "years ago")
    print("start:", data.index[start])

    baseline = INITIAL_INVESTMENT
    optimized = INITIAL_INVESTMENT
    isInvested = True                 # start off invested the market
    transactionCount = 0

    for day in range(start, len(data)):
        daily_return = data['Close'][day] / data['Close'][day-1]    # daily return

        if isInvested:                    # is our money in VOO?
          optimized *= daily_return
          if Sell(day, data):             # should we sell at close?
            print(f"Selling at {data['Close'][day]}, {data.index[day]}")
            isInvested = False
            transactionCount+=1

        else:                           # not currently invested
          optimized *= 1              # 0% interest rate
          if Buy(day, data):            # should we buy at close?
            print(f"Buying at {data['Close'][day]}, {data.index[day]}")
            isInvested = True
            transactionCount+=1

        baseline *= daily_return      # update baseline value

    RESULTS[f"Baseline {years_ago}"] = baseline
    RESULTS[f"Optimized {years_ago}"] = optimized, transactionCount
    print()
    print()

"""# Simulation & Results"""

MainSimulation(data)

diffs = Performance(RESULTS)

"""# Data Visualization"""

fig = px.line(data, x='Date', y=["Close", "sma_200", "sma_50", "bb_Hband", "bb_Lband", "sma_500"])
fig.show()

fig = px.line(data, x='Date', y=["rsi", 'rsi_l'])
fig.show()

fig = px.line(data, x='Date', y=["mac_dif", 'mac', 'mac_ind'])
fig.show()

data

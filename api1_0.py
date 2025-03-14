# -*- coding: utf-8 -*-
"""API1.0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Ewl4tpvcFii0U-un6lXewNSK0SArXKLn
"""

!pip install pandas ta requests

import requests
import time
import pandas as pd
import ta

# ✅ Initial Paper Trading Setup
capital = 100000  # ₹1,00,000 starting capital
btc_holdings = 0  # Start with no BTC
buy_price = None  # Store last buy price
price_history = []  # Store prices for SMA, RSI, MACD calculation

# ✅ Trading Parameters
SMA_WINDOW = 10  # 10-period SMA
BUY_RSI_THRESHOLD = 35  # RSI < 35 → Buy
SELL_RSI_THRESHOLD = 55  # RSI > 55 → Sell

print("🔹 Starting Paper Trading with SMA, RSI, MACD...")

while True:
    try:
        # ✅ Fetch BTC/USDT Price from OKX
        okx_url = "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT"
        okx_response = requests.get(okx_url).json()
        btc_usdt = float(okx_response["data"][0]["last"])

        # ✅ Fetch USD/INR Conversion Rate
        usd_inr_url = "https://api.exchangerate-api.com/v4/latest/USD"
        usd_inr = requests.get(usd_inr_url).json()["rates"]["INR"]

        # ✅ Convert BTC/USDT to BTC/INR
        btc_inr = btc_usdt * usd_inr
        print(f"\n🔹 Live BTC/INR Price: ₹{btc_inr:.2f}")

        # ✅ Store Price in History (Keep only last 50 records)
        price_history.append(btc_inr)
        if len(price_history) > 50:
            price_history.pop(0)

        # ✅ Only calculate indicators if we have enough data
        if len(price_history) >= SMA_WINDOW:
            df = pd.DataFrame(price_history, columns=["close"])

            # ✅ Calculate Indicators
            df["SMA"] = df["close"].rolling(SMA_WINDOW).mean()
            df["RSI"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
            macd = ta.trend.MACD(df["close"], window_slow=26, window_fast=12, window_sign=9)
            df["MACD"] = macd.macd()
            df["Signal"] = macd.macd_signal()

            latest_price = df["close"].iloc[-1]
            latest_sma = df["SMA"].iloc[-1]
            latest_rsi = df["RSI"].iloc[-1]
            latest_macd = df["MACD"].iloc[-1]
            latest_signal = df["Signal"].iloc[-1]

            print(f"📊 SMA: {latest_sma:.2f} | RSI: {latest_rsi:.2f} | MACD: {latest_macd:.2f} | Signal: {latest_signal:.2f}")

            # ✅ Buy Condition: Price > SMA & RSI < 35 & MACD > Signal
            if latest_price > latest_sma and latest_rsi < BUY_RSI_THRESHOLD and latest_macd > latest_signal and capital > 0:
                btc_holdings = capital / latest_price
                buy_price = latest_price
                capital = 0
                print(f"✅ BOUGHT {btc_holdings:.6f} BTC at ₹{buy_price:.2f}")

            # ✅ Sell Condition: Price < SMA & RSI > 55 & MACD < Signal
            elif latest_price < latest_sma and latest_rsi > SELL_RSI_THRESHOLD and latest_macd < latest_signal and btc_holdings > 0:
                capital = btc_holdings * latest_price
                print(f"✅ SOLD {btc_holdings:.6f} BTC at ₹{latest_price:.2f} → New Balance: ₹{capital:.2f}")
                btc_holdings = 0
                buy_price = None

            # ✅ Show Portfolio Balance
            net_worth = capital if btc_holdings == 0 else btc_holdings * latest_price
            print(f"💰 Capital: ₹{capital:.2f} | BTC Holdings: {btc_holdings:.6f} BTC | Net Worth: ₹{net_worth:.2f}")

        time.sleep(10)  # Wait 10 seconds before checking again

    except Exception as e:
        print(f"❌ Error: {e}")
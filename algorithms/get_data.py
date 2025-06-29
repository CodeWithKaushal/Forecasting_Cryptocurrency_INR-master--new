import yfinance as yf
import pandas as pd
import requests
import json
import time
from datetime import datetime, timedelta
import numpy as np
# To disable SettingWithCopyWarning
pd.options.mode.chained_assignment = None  # default='warn'


def crypto_data(ticker, period, intervals):
    """
    Fetch cryptocurrency data with robust error handling and fallback options.
    """
    try:
        # Try with original parameters first
        df = yf.download(ticker, period=period, interval=intervals, progress=False)
        
        # Check if data is empty or insufficient
        if df.empty or len(df) < 100:
            print(f"Insufficient data for {ticker} with {period}/{intervals}, trying fallback...")
            
            # Try different time periods as fallback
            fallback_configs = [
                ('2mo', '1h'),     # 2 months with 1-hour intervals
                ('1mo', '1h'),     # 1 month with 1-hour intervals
                ('1mo', '90m'),    # 1 month with 90-minute intervals
                ('2mo', '2h'),     # 2 months with 2-hour intervals
                ('6mo', '1d'),     # 6 months with daily intervals
            ]
            
            for fb_period, fb_interval in fallback_configs:
                try:
                    df = yf.download(ticker, period=fb_period, interval=fb_interval, progress=False)
                    if not df.empty and len(df) >= 100:
                        print(f"Successfully fetched data with {fb_period}/{fb_interval}")
                        period, intervals = fb_period, fb_interval
                        break
                except Exception as e:
                    continue
            
            # If still no data, raise an error
            if df.empty or len(df) < 100:
                raise ValueError(f"No sufficient data available for {ticker}")
        
        # Create future time slots based on the interval
        prediction_hours = 15  # Standardize to 15 hours for both LSTM and ARIMA
        
        # Determine time delta based on interval
        if 'h' in intervals:
            hours = int(intervals.replace('h', '').replace('m', ''))
            if 'm' in intervals:  # Handle cases like '90m'
                hours = int(intervals.replace('m', '')) / 60
            time_delta = pd.Timedelta(hours=hours)
        elif 'm' in intervals:
            minutes = int(intervals.replace('m', ''))
            time_delta = pd.Timedelta(minutes=minutes)
        elif 'd' in intervals:
            days = int(intervals.replace('d', ''))
            time_delta = pd.Timedelta(days=days)
        else:
            time_delta = pd.Timedelta(hours=1)  # Default fallback
        
        # Add future timestamps for predictions
        for i in range(prediction_hours):
            last_date = df.index[-1] + time_delta
            empty_row = pd.DataFrame(columns=df.columns, index=[last_date])
            df = pd.concat([df, empty_row])
        
        # Clean up the dataframe
        df = df.drop(columns=['Open', 'High', 'Low', 'Adj Close', 'Volume'], errors='ignore')
        df.index.name = 'Datetime'
        df_pred = df.copy()
        
        # Remove rows with all NaN values except for the prediction slots
        original_length = len(df) - prediction_hours
        df_clean = df.iloc[:original_length].dropna()
        
        # Rebuild with clean historical data + prediction slots
        prediction_slots = df.iloc[original_length:]
        df_final = pd.concat([df_clean, prediction_slots])
        
        print(f"Data fetched successfully: {len(df_clean)} historical points, {prediction_hours} prediction slots")
        return df_final, df_final.copy()
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")


# def get_Data():
#     data = yf.download(tickers='BTC-INR, ETH-INR, LTC-INR', period='1mo', interval="15m",
#                        group_by='ticker')
#     # print(eth)
#     # tickers = yf.Tickers('BTC-INR, ETH-INR,LTC-INR')
#     # print(tickers.tickers)
#       print(tickers.tickers['BTC-INR'].info)
#     # ltc = tickers.tickers['LTC-INR'].history(period="1m",interval="5m")
#     btc = data['BTC-INR']
#     eth = data['ETH-INR']
#     ltc = data['LTC-INR']
#     df_btc = btc.dropna()
#     df_btc.reset_index(inplace=True)
#     df_btc["closeDiff"] = df_btc["Close"].diff()
#     # df_btc['Datetime'] = pd.to_datetime(df_btc['Datetime'], unit='s')
#     print(df_btc)
#
#     # df_btc.plot(x='Datetime',y='Close')
#     plt.plot(df_btc['Datetime'], df_btc['Close'], color='blue', label='Trend')
#     plt.show()

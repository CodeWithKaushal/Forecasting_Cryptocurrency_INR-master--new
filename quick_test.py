#!/usr/bin/env python3
"""
Quick test to verify the new crypto_data function works
"""

from algorithms.get_data import crypto_data

def quick_test():
    print("Testing BTC-USD data fetching...")
    try:
        df, df_pred = crypto_data('BTC-USD', '3mo', '60m')
        if df is not None:
            historical = df.dropna(subset=['Close'])
            print(f"Success! Got {len(historical)} historical data points")
            print(f"Total DataFrame length: {len(df)} (includes prediction slots)")
            print(f"Last price: ${historical['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("Failed - no data returned")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    quick_test()

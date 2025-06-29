#!/usr/bin/env python3
"""
Test script to verify that the multiple data sources are working properly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from algorithms.get_data import get_coingecko_data, get_binance_data, crypto_data, generate_sample_data

def test_data_sources():
    print("Testing cryptocurrency data sources...")
    print("=" * 50)
    
    ticker = "BTC-USD"
    
    # Test 1: CoinGecko
    print("1. Testing CoinGecko API...")
    try:
        data = get_coingecko_data(ticker, days=1)
        if data is not None and len(data) > 0:
            print(f"   ✅ Success: {len(data)} data points")
            print(f"   Latest price: ${data['Close'].iloc[-1]:.2f}")
        else:
            print("   ❌ Failed: No data returned")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: Binance
    print("2. Testing Binance API...")
    try:
        data = get_binance_data(ticker, limit=24)
        if data is not None and len(data) > 0:
            print(f"   ✅ Success: {len(data)} data points")
            print(f"   Latest price: ${data['Close'].iloc[-1]:.2f}")
        else:
            print("   ❌ Failed: No data returned")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 3: Sample data generation
    print("3. Testing sample data generation...")
    try:
        data = generate_sample_data(ticker, hours=24)
        if data is not None and len(data) > 0:
            print(f"   ✅ Success: {len(data)} data points")
            print(f"   Sample price: ${data['Close'].iloc[-1]:.2f}")
        else:
            print("   ❌ Failed: No data generated")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 4: Main crypto_data function
    print("4. Testing main crypto_data function...")
    try:
        df, df_pred = crypto_data(ticker, '3mo', '60m')
        if df is not None and len(df) > 0:
            historical_data = df.dropna(subset=['Close'])
            print(f"   ✅ Success: {len(historical_data)} historical data points")
            print(f"   Total dataframe length: {len(df)} (includes prediction slots)")
            if len(historical_data) > 0:
                print(f"   Latest price: ${historical_data['Close'].iloc[-1]:.2f}")
        else:
            print("   ❌ Failed: No data returned")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("=" * 50)
    print("Data source testing completed!")

if __name__ == "__main__":
    test_data_sources()

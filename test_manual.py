#!/usr/bin/env python3
"""
Manual data source tester - allows you to test individual APIs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_coingecko():
    """Test CoinGecko API"""
    from algorithms.get_data import get_coingecko_data
    
    print("Testing CoinGecko API...")
    try:
        data = get_coingecko_data('BTC-USD', days=1)
        if data is not None and len(data) > 0:
            print(f"✅ CoinGecko Success: {len(data)} data points")
            print(f"   Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
            print(f"   Latest: ${data['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("❌ CoinGecko Failed: No data")
            return False
    except Exception as e:
        print(f"❌ CoinGecko Error: {e}")
        return False

def test_binance():
    """Test Binance API"""
    from algorithms.get_data import get_binance_data
    
    print("Testing Binance API...")
    try:
        data = get_binance_data('BTC-USD', limit=24)
        if data is not None and len(data) > 0:
            print(f"✅ Binance Success: {len(data)} data points")
            print(f"   Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
            print(f"   Latest: ${data['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("❌ Binance Failed: No data")
            return False
    except Exception as e:
        print(f"❌ Binance Error: {e}")
        return False

def test_sample_data():
    """Test sample data generation"""
    from algorithms.get_data import generate_sample_data
    
    print("Testing Sample Data Generation...")
    try:
        data = generate_sample_data('BTC-USD', hours=24)
        if data is not None and len(data) > 0:
            print(f"✅ Sample Data Success: {len(data)} data points")
            print(f"   Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
            print(f"   Latest: ${data['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("❌ Sample Data Failed")
            return False
    except Exception as e:
        print(f"❌ Sample Data Error: {e}")
        return False

def test_main_function():
    """Test the main crypto_data function"""
    from algorithms.get_data import crypto_data
    
    print("Testing Main crypto_data Function...")
    try:
        df, df_pred = crypto_data('BTC-USD', '3mo', '60m')
        if df is not None:
            historical = df.dropna(subset=['Close'])
            print(f"✅ Main Function Success: {len(historical)} historical points")
            print(f"   Total length: {len(df)} (includes prediction slots)")
            print(f"   Latest price: ${historical['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("❌ Main Function Failed: No data")
            return False
    except Exception as e:
        print(f"❌ Main Function Error: {e}")
        return False

def main():
    print("Cryptocurrency Data Source Tester")
    print("=" * 40)
    
    results = {}
    
    print("\n1. Individual API Tests:")
    print("-" * 25)
    results['coingecko'] = test_coingecko()
    print()
    results['binance'] = test_binance()
    print()
    results['sample'] = test_sample_data()
    
    print("\n2. Main Function Test:")
    print("-" * 20)
    results['main'] = test_main_function()
    
    print("\n" + "=" * 40)
    print("SUMMARY:")
    for source, success in results.items():
        status = "✅ Working" if success else "❌ Failed"
        print(f"  {source.capitalize()}: {status}")
    
    working_sources = sum(results.values())
    print(f"\nWorking Sources: {working_sources}/4")
    
    if working_sources > 0:
        print("🎉 At least one data source is working - your app should function!")
    else:
        print("⚠️  No data sources working - check your internet connection")

if __name__ == "__main__":
    main()

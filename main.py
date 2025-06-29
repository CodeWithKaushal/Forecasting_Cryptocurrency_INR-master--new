from algorithms import *
from flask import Flask, render_template, jsonify
from werkzeug.exceptions import HTTPException

app = Flask(__name__)


def get_candles(df, df_pred):
    data = []
    data_pred = []
    try:
        for row in df_pred.iterrows():
            row_data = {'date': row[1]['Datetime'], 'close': row[1]['Close']}
            data_pred.append(row_data)
        for row in df.iterrows():
            row_data = {'date': row[1]['Datetime'], 'close': row[1]['Close']}
            data.append(row_data)
    except Exception as e:
        print(e)
    return [data, data_pred]


@app.route('/getJson/<ticker>/<algorithm>', methods=['GET'])
def get_json_data(ticker='BTC-USD', algorithm='LSTM'):
    try:
        print(f"Fetching data for {ticker} using {algorithm} algorithm...")
        
        # Get data with better error handling
        df, df_pred = crypto_data(ticker, '3mo', "60m")
        
        # Validate data more thoroughly
        if df is None or df.empty:
            raise ValueError("No data received from API")
            
        # Remove any rows where all values are NaN
        df_historical = df.dropna(subset=['Close'])
        
        if len(df_historical) < 50:
            raise ValueError(f"Insufficient historical data: only {len(df_historical)} valid points")
        
        # Prepare clean historical data
        df_clean = df_historical.copy()
        df_clean.reset_index(inplace=True)
        
        # Ensure datetime column exists and is properly formatted
        if 'Datetime' not in df_clean.columns:
            df_clean['Datetime'] = df_clean.index
            
        df_clean['Datetime'] = pd.to_datetime(df_clean['Datetime']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"Historical data points: {len(df_clean)}")

        # Select algorithm based on parameter
        try:
            if algorithm.upper() == 'LSTM':
                pred_values, rmse_value = lstm(df_clean)
            elif algorithm.upper() == 'ARIMA':
                pred_values, rmse_value = arima(df_clean)
            else:
                pred_values, rmse_value = lstm(df_clean)  # Default to LSTM
        except Exception as algo_error:
            print(f"Algorithm error: {algo_error}")
            raise ValueError(f"Algorithm {algorithm} failed: {str(algo_error)}")

        # Validate prediction results
        if pred_values is None or len(pred_values) == 0:
            raise ValueError("Algorithm failed to generate predictions")

        # Handle prediction values shape
        if hasattr(pred_values, 'ndim') and pred_values.ndim > 1:
            pred_values = pred_values.flatten()
        
        # Ensure we have a reasonable number of predictions (limit to 15)
        if len(pred_values) > 15:
            pred_values = pred_values[:15]
        elif len(pred_values) < 5:
            # If too few predictions, pad with the last value
            last_val = pred_values[-1] if len(pred_values) > 0 else df_clean['Close'].iloc[-1]
            pred_values = np.append(pred_values, [last_val] * (5 - len(pred_values)))

        print(f"Generated {len(pred_values)} predictions")

        # Create future dates for predictions
        last_date = pd.to_datetime(df_clean['Datetime'].iloc[-1])
        future_dates = []
        for i in range(len(pred_values)):
            future_date = last_date + pd.Timedelta(hours=i+1)
            future_dates.append(future_date.strftime('%Y-%m-%d %H:%M:%S'))

        # Create prediction dataframee
        df_pred_only = pd.DataFrame({
            'Datetime': future_dates,
            'Close': pred_values
        })

        # Include RMSE in response
        result = get_candles(df_clean, df_pred_only)
        result.append({
            'rmse': float(rmse_value) if rmse_value is not None else 0.0,
            'algorithm': algorithm.upper(),
            'historical_points': len(df_clean),
            'prediction_points': len(df_pred_only),
            'ticker': ticker,
            'last_price': float(df_clean['Close'].iloc[-1]),
            'prediction_range': f"{float(min(pred_values)):.2f} - {float(max(pred_values)):.2f}"
        })

        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except ValueError as ve:
        print(f"Validation error: {ve}")
        error_response = jsonify({
            'error': str(ve),
            'type': 'validation_error',
            'suggestion': 'Try a different cryptocurrency or check if the market is open'
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 400
        
    except Exception as e:
        print(f"Error in get_json_data: {e}")
        import traceback
        traceback.print_exc()
        
        error_response = jsonify({
            'error': f'Internal server error: {str(e)}',
            'type': 'server_error',
            'suggestion': 'Please try again in a few moments'
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500


@app.route('/', methods=['GET'])
def index():
    return render_template('plot.html')


@app.route('/info', methods=['GET'])
def index2():
    return render_template('info.html')


@app.errorhandler(Exception)
def internal_error(error):
    code = 500
    print(error.args)
    if isinstance(error, HTTPException):
        code = error.code
    return '', code


app.run(host="0.0.0.0", port=5000, debug=True)  # ssl_context="adhoc"

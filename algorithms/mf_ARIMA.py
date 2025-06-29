from algorithms import *
import warnings
warnings.filterwarnings('ignore', 'statsmodels.tsa.arima_model.ARMA',
                        FutureWarning)
warnings.filterwarnings('ignore', 'statsmodels.tsa.arima_model.ARIMA',
                        FutureWarning)


def arima(df):
    days = 15  # Changed to match LSTM prediction length
    df_new = df['Close'].astype(float)  # Changed from 'nav' to 'Close'

    X = df_new.values
    size = int(len(X) * 0.90)
    train, test = X[0:size], X[size:len(X)]
    history = [x for x in train]
    prediction = list()
    for t in range(len(test)):
        model = ARIMA(history, order=(5, 1, 0))
        model_fit = model.fit()
        output = model_fit.forecast()
        yhat = output[0]
        prediction.append(yhat)
        obs = test[t]
        history.append(obs)
    rmse = math.sqrt(mean_squared_error(test, prediction))

    # Actual forecasting
    history = [x for x in X]
    forecasting = []
    for i in range(days):
        model = ARIMA(history, order=(5, 1, 0))
        model_fit = model.fit()
        output = model_fit.forecast()
        yhat = output[0]
        forecasting.append(yhat)  # future day
        history.append(yhat)

    return forecasting, rmse

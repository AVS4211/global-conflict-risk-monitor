import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def get_forecast(data):

    series = pd.Series(data)

    # safety check
    if len(series) < 5:
        return [series.iloc[-1]] * 3

    model = ARIMA(series, order=(1,1,1))
    model_fit = model.fit()

    forecast = model_fit.forecast(steps=3)

    return forecast.tolist()
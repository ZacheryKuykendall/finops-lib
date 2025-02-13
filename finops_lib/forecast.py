import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import logging

logger = logging.getLogger(__name__)

def forecast_costs(cost_df: pd.DataFrame, n_days: int = 30) -> pd.DataFrame:
    """
    Forecast future costs using linear regression.
    Assumes cost_df has a 'timestamp' column convertible to ordinal numbers.
    """
    try:
        df = cost_df.copy()
        df['date'] = pd.to_datetime(df['timestamp'])
        df['ordinal'] = df['date'].apply(lambda x: x.toordinal())
        X = df[['ordinal']]
        y = df['cost']
        
        model = LinearRegression()
        model.fit(X, y)
        
        last_date = df['date'].max()
        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, n_days+1)]
        future_ordinals = [[d.toordinal()] for d in future_dates]
        predictions = model.predict(future_ordinals)
        
        forecast_df = pd.DataFrame({"date": future_dates, "forecast_cost": predictions})
        return forecast_df
    except Exception as e:
        logger.error("Forecasting failed: %s", e)
        raise

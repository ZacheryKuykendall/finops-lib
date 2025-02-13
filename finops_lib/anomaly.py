import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def detect_anomalies(cost_df: pd.DataFrame, threshold: float = 2.0) -> pd.DataFrame:
    """
    Detect anomalies in cost data based on a simple standard deviation rule.
    """
    try:
        mean_cost = cost_df["cost"].mean()
        std_cost = cost_df["cost"].std()
        cost_df["anomaly"] = np.abs(cost_df["cost"] - mean_cost) > threshold * std_cost
        return cost_df[cost_df["anomaly"]]
    except Exception as e:
        logger.error("Anomaly detection failed: %s", e)
        raise

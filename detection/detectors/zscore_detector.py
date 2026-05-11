import numpy as np
from scipy.stats import zscore

from detection.detectors.base_detector import BaseDetector

class ZScoreDetector(BaseDetector):

    def detect(self, df, metric_col):

        values = df[metric_col].astype(float)

        df["anomaly_score"] = zscore(values)

        anomalies = df[
            np.abs(df["anomaly_score"]) >= 3
        ]

        return anomalies

import numpy as np

from detection.detectors.base_detector import BaseDetector

class RollingWindowDetector(BaseDetector):

    def detect(self, df, metric_col):

        rolling_mean = (
            df[metric_col]
            .rolling(window=7)
            .mean()
        )

        rolling_std = (
            df[metric_col]
            .rolling(window=7)
            .std()
        )

        df["anomaly_score"] = (
            df[metric_col] - rolling_mean
        ) / rolling_std

        anomalies = df[
            np.abs(df["anomaly_score"]) >= 2.5
        ]

        return anomalies

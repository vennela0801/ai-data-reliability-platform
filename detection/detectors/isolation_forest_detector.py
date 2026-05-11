from sklearn.ensemble import IsolationForest

from detection.detectors.base_detector import BaseDetector

class IsolationForestDetector(BaseDetector):

    def detect(self, df, metric_col):

        model = IsolationForest(
            contamination=0.05,
            random_state=42
        )

        df["prediction"] = model.fit_predict(
            df[[metric_col]]
        )

        anomalies = df[
            df["prediction"] == -1
        ]

        anomalies["anomaly_score"] = -1

        return anomalies

from detection.detectors.base_detector import BaseDetector

class IQRDetector(BaseDetector):

    def detect(self, df, metric_col):

        Q1 = df[metric_col].quantile(0.25)
        Q3 = df[metric_col].quantile(0.75)

        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        anomalies = df[
            (df[metric_col] < lower)
            |
            (df[metric_col] > upper)
        ]

        anomalies["anomaly_score"] = (
            anomalies[metric_col] - Q1
        ) / IQR

        return anomalies

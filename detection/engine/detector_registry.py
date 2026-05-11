from detection.detectors.zscore_detector import ZScoreDetector
from detection.detectors.iqr_detector import IQRDetector
from detection.detectors.rolling_detector import RollingWindowDetector
from detection.detectors.isolation_forest_detector import IsolationForestDetector

DETECTORS = {
    "zscore": ZScoreDetector(),
    "iqr": IQRDetector(),
    "rolling": RollingWindowDetector(),
    "isolation_forest": IsolationForestDetector()
}

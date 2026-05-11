from alerts.slack.slack_alert_service import (
    send_slack_alert
)

send_slack_alert(
    severity="critical",
    detector="zscore",
    metric="total_revenue",
    score=7.82,
    explanation="""
Potential duplicated transaction ingestion
or checkout pricing regression detected.

Recommended:
- validate upstream transaction ingestion
- inspect pricing service deployments
- verify duplicate order ingestion
"""
)

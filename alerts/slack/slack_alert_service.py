import os
import requests
from dotenv import load_dotenv

# ---------------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------------

load_dotenv(
    os.path.expanduser(
        "~/ai-data-reliability-platform/.env"
    )
)

SLACK_WEBHOOK_URL = os.getenv(
    "SLACK_WEBHOOK_URL"
)

# ---------------------------------------------------------
# Slack Alert Sender
# ---------------------------------------------------------

def send_slack_alert(
    severity,
    detector,
    metric,
    score,
    explanation
):

    emoji = {
        "critical": "🚨",
        "high": "⚠️",
        "medium": "🟡",
        "low": "🔵"
    }.get(severity, "⚪")

    message = f'''
{emoji} *DATA INCIDENT DETECTED*

*Severity:* {severity.upper()}
*Detector:* {detector}
*Metric:* {metric}
*Anomaly Score:* {round(score, 2)}

*AI Root Cause Analysis*
{explanation}
'''

    payload = {
        "text": message
    }

    response = requests.post(
        SLACK_WEBHOOK_URL,
        json=payload
    )

    if response.status_code == 200:

        print(
            "✅ Slack alert sent successfully"
        )

    else:

        print(
            f"❌ Slack alert failed: "
            f"{response.text}"
        )

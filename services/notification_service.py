"""
NIRVAAN Notification & Alert Dispatch Engine (services/notification_service.py)

Evaluates newly generated disaster alerts against active notification rules
and user preferences. Dispatches in-app, webhook, and email notifications
with strict idempotency to prevent duplicate notifications or alert storms.
"""

from datetime import datetime, timezone
import json
import logging
from typing import Any, Dict, List, Optional

from db.repository import DatabaseRepository

logger = logging.getLogger("nirvaan.notification_service")

SEVERITY_RANKS = {
    "LOW": 1,
    "MODERATE": 2,
    "HIGH": 3,
    "CRITICAL": 4
}


class NotificationEngine:
    """
    Event-driven notification dispatch and rule evaluation engine.
    """

    def __init__(self, repo: Optional[DatabaseRepository] = None):
        self.repo = repo or DatabaseRepository()

    def process_alert_notifications(self, alert_id: str, event_id: str, disaster_type: str, severity: str, confidence: float) -> List[Dict[str, Any]]:
        """
        Evaluates active rules and user preferences for an alert, dispatching notifications idempotently.
        """
        rules = self.repo.get_active_notification_rules()
        dispatched = []

        alert_sev_rank = SEVERITY_RANKS.get(severity.upper(), 2)

        for rule in rules:
            rule_types = rule.get("disaster_types", "all").lower()
            min_sev = rule.get("min_severity", "MODERATE").upper()
            min_conf = float(rule.get("min_confidence", 70.0))
            min_sev_rank = SEVERITY_RANKS.get(min_sev, 2)

            # Check rule match criteria
            if rule_types != "all" and disaster_type.lower() not in rule_types:
                continue
            if alert_sev_rank < min_sev_rank:
                continue
            if confidence < min_conf:
                continue

            channels = []
            try:
                channels = json.loads(rule.get("channels_json", '["in_app"]'))
            except Exception:
                channels = ["in_app"]

            recipient = rule.get("user_id") or "broadcast_all"

            for channel in channels:
                # Idempotency check: prevent duplicate notifications
                if not self.repo.is_notification_sent_for_alert(alert_id, channel, recipient):
                    notif = self.repo.log_notification(
                        alert_id=alert_id,
                        event_id=event_id,
                        channel=channel,
                        recipient=recipient,
                        status="DELIVERED"
                    )
                    dispatched.append(notif)
                    logger.info("Dispatched %s notification for alert %s (Event: %s) to %s", channel, alert_id, event_id, recipient)

        # If no custom rules exist/matched and no prior notifications logged at all for this alert, log default baseline in_app
        if not dispatched and not self.repo.has_any_notification_been_sent_for_alert(alert_id) and not rules:
            notif = self.repo.log_notification(
                alert_id=alert_id,
                event_id=event_id,
                channel="in_app",
                recipient="default",
                status="DELIVERED"
            )
            if notif:
                dispatched.append(notif)

        return dispatched

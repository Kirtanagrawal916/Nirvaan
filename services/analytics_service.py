"""
NIRVAAN Advanced Analytics Service (services/analytics_service.py)

Exposes aggregated analytics on disaster frequency, severity distributions,
temporal timeseries, and geospatial clustering from real database records.
"""

from typing import Any, Dict, List, Optional

from db.repository import DatabaseRepository


class AnalyticsService:
    """
    Computes statistical and geospatial analytics over real disaster records.
    """

    def __init__(self, repo: Optional[DatabaseRepository] = None):
        self.repo = repo or DatabaseRepository()

    def get_overview(self, days: int = 30) -> Dict[str, Any]:
        """Returns overview counts and distributions."""
        return self.repo.get_analytics_overview(days=days)

    def get_timeseries(self, days: int = 30) -> List[Dict[str, Any]]:
        """Returns temporal incident counts over time."""
        return self.repo.get_analytics_timeseries(days=days)

    def get_disaster_distribution(self) -> Dict[str, Any]:
        """Returns disaster type frequency breakdown."""
        overview = self.repo.get_analytics_overview()
        return {
            "distribution": overview.get("disaster_type_distribution", {}),
            "severity": overview.get("severity_distribution", {}),
            "total_events": overview.get("total_disasters_tracked", 0)
        }

    def get_geographic_hotspots(self) -> List[Dict[str, Any]]:
        """Returns geographic clusters of disaster occurrences."""
        return self.repo.get_analytics_geographic_clusters()

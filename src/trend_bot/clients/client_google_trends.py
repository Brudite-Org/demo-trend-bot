from typing import Any, Dict, List
from trend_bot.config import settings
import requests

class GoogleTrendsClient:
    BASE_URL = settings.SERP_BASE_URL

    def __init__(self, api_key: str | None = None, timeout: int = 10):
        # Pull from environment or settings, falling back if needed
        self.api_key = api_key
        self.timeout = timeout

    def search(self, keyword: str, geo: str = "IN", date: str = "now 7-d", data_type: str = "TIMESERIES", hl: str = "en") -> Dict[str, Any]:
        params: dict[str, Any] = {
            "engine": "google_trends",
            "q": keyword,
            "geo": geo,
            "date": date,
            "data_type": data_type,
            "hl": hl,
            "api_key": self.api_key,
        }

        response = requests.get(self.BASE_URL, params=params, timeout=self.timeout)

        if not response.ok:
            try:
                error_data = response.json()
                error_message = error_data.get("error", response.text)
            except ValueError:
                error_message = response.text
            raise RuntimeError(f"SerpApi HTTP {response.status_code}: {error_message}")

        try:
            data = response.json()
        except ValueError as e:
            raise RuntimeError(f"SerpApi returned invalid JSON: {response.text[:500]}") from e

        if "error" in data:
            raise RuntimeError(f"SerpApi error: {data['error']}")

        return data

    def get_related_queries(self, keyword: str, geo: str = "IN", date: str = "now 7-d") -> Dict[str, Any]:
        return self.search(keyword=keyword, geo=geo, date=date, data_type="RELATED_QUERIES")

    def get_related_topics(self, keyword: str, geo: str = "IN", date: str = "now 7-d") -> Dict[str, Any]:
        return self.search(keyword=keyword, geo=geo, date=date, data_type="RELATED_TOPICS")

    def get_interest_over_time(self, keywords: List[str], geo: str = "IN", date: str = "now 7-d") -> Dict[str, Any]:
        if not keywords:
            return {}
        if len(keywords) > 5:
            raise ValueError("TIMESERIES supports a maximum of 5 keywords.")
        keyword_query = ",".join(keywords)
        return self.search(keyword=keyword_query, geo=geo, date=date, data_type="TIMESERIES")
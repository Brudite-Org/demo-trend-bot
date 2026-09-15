from sqlalchemy.orm import Session
from typing import Any, Dict, List

from trend_bot.clients.client_google_trends import google_client
from trend_bot.database.database import GoogleTrendsModel

class GoogleTrendsCollector:
    """Collects and organizes Google Trends data for multiple keywords."""

    def __init__(self, api_key: str | None = None, geo: str = "IN", date: str = "now 7-d"):
        self.api_key = api_key
        self.geo = geo
        self.date = date 
        self.client = google_client

    def collect_keyword_info(self, keyword: str) -> Dict[str, Any]:
        """Collect all trend information for one keyword."""
        print(f"Collecting Google Trends: {keyword}")
        related_queries = self.client.get_related_queries(keyword=keyword, geo=self.geo, date=self.date)
        related_topics = self.client.get_related_topics(keyword=keyword, geo=self.geo, date=self.date)

        return {
            "keyword": keyword,
            "related_queries": related_queries.get("related_queries", {"top": [], "rising": []}),
            "related_topics": related_topics.get("related_topics", {"top": [], "rising": []}),
        }

    def collect(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Collect related queries, topics, and timeseries for every keyword."""
        results: list[dict[str, Any]] = []
        cleaned_keywords: list[str] = []

        for keyword in keywords:
            keyword_stripped = keyword.strip()
            if keyword and keyword_stripped not in cleaned_keywords:
                cleaned_keywords.append(keyword_stripped)

        for keyword in cleaned_keywords:
            try:
                result = self.collect_keyword_info(keyword)
                results.append(result)
            except Exception as e:
                print(f"Failed to collect {keyword}: {e}")
                results.append({"keyword": keyword, "error": str(e)})

        if cleaned_keywords:
            try:
                timeseries = self.client.get_interest_over_time(
                    keywords=cleaned_keywords[:5], geo=self.geo, date=self.date
                )
                self._attach_timeseries(results, timeseries)
            except Exception as e:
                print(f"Failed to collect interest over time: {e}")

        return results

    def save_to_db(self, db: Session, results: List[Dict[str, Any]]) -> None:
        """Persists collected payloads into PostgreSQL."""
        for result in results:
            if "error" in result:
                continue
            db_record = GoogleTrendsModel(
                keyword=result.get("keyword"),
                geo=self.geo,
                date_range=self.date,
                related_queries=result.get("related_queries"),
                related_topics=result.get("related_topics"),
                interest_over_time=result.get("interest_over_time")
            )
            db.add(db_record)
        db.commit()
    
    def format_summary(self, results: List[Dict[str, Any]]) -> str:
        """Converts structured Google Trends data into a text block for Gemini."""
        lines = ["[Google Trends Search Intelligence]"]
        for result in results:
            keyword = result.get("keyword")
            if "error" in result:
                lines.append(f"Keyword '{keyword}': Error ({result['error']})")
                continue
            lines.append(f"Keyword: '{keyword}'")
            
            rising = result.get("related_queries", {}).get("rising", [])
            if rising:
                top_rising = [q.get("query") for q in rising[:3]]
                lines.append(f"Rising Queries: {', '.join(top_rising)}")

            top = result.get("related_queries", {}).get("top", [])
            if top:
                top_top = [q.get("query") for q in top[:3]]
                lines.append(f"Top Queries: {', '.join(top_top)}")

            timeline = result.get("interest_over_time", [])
            if timeline:
                latest = timeline[-1]
                lines.append(f"Current Interest Index: {latest.get('extracted_value', 'N/A')}/100")
                
        return "\n".join(lines)

    @staticmethod
    def _attach_timeseries(results: List[Dict[str, Any]], timeseries: Dict[str, Any]) -> None:
        """Attach interest-over-time data to each corresponding keyword."""
        interest_data = timeseries.get("interest_over_time", {})
        timeline_data = interest_data.get("timeline_data", [])

        for result in results:
            keyword = result["keyword"]
            keyword_timeline: list[dict[str, Any]] = []

            for point in timeline_data:
                values = point.get("values", [])
                for value in values:
                    if value.get("query") == keyword:
                        keyword_timeline.append({
                            "date": point.get("date"),
                            "timestamp": point.get("timestamp"),
                            "value": value.get("value"),
                            "extracted_value": value.get("extracted_value"),
                        })
            result["interest_over_time"] = keyword_timeline
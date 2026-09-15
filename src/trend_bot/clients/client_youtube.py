import requests
from typing import Any
from trend_bot.models import Video
from trend_bot.config import settings
from datetime import datetime, timedelta, timezone

class YouTubeClient:
    BASE_URL = settings.YOUTUBE_BASE_URL

    def __init__(self, api_key: str | None):
        self.api_key = api_key

    def search_videos(self, query: str | list[str], max_results: int = 5) -> list[Video]:

        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        published_after = seven_days_ago.isoformat().replace("+00:00", "Z")

        # If a list of keywords is passed, automatically join them with OR
        if isinstance(query, list):
            query = " OR ".join(query)

        search_url = f"{self.BASE_URL}/search"
        videos: list[Video] = []
        page_token = None

        while len(videos) < max_results:
            per_page = min(max_results - len(videos), 50)
            params: dict[str, Any] = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": per_page,
                "publishedAfter": published_after,
                "key": self.api_key,
            }
            if page_token:
                params["pageToken"] = page_token

            response = requests.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            if not items:
                break

            for item in items:
                if "videoId" in item.get("id", {}):
                    video = Video(
                        video_id=item["id"]["videoId"],
                        title=item["snippet"]["title"],
                        description=item["snippet"]["description"],
                        channel_id=item["snippet"]["channelId"],
                        channel_title=item["snippet"]["channelTitle"],
                        published_at=item["snippet"]["publishedAt"],
                    )
                    videos.append(video)

            page_token = data.get("nextPageToken")
            if not page_token or len(videos) >= max_results:
                break

        if not videos:
            return []

        return self._enrich_video_statistics(videos[:max_results])

    def _enrich_video_statistics(self, videos: list[Video]) -> list[Video]:
        video_ids = [video.video_id for video in videos]
        stats_url = f"{self.BASE_URL}/videos"
        stats_params: dict[str, Any] = {
            "part": "statistics",
            "id": ",".join(video_ids),
            "key": self.api_key,
        }

        response = requests.get(url=stats_url, params=stats_params)
        response.raise_for_status()
        stats_data = response.json()

        statistics_by_id = {
            item["id"]: item["statistics"]
            for item in stats_data.get("items", [])
        }

        enriched_videos: list[Video] = []
        for video in videos:
            stats = statistics_by_id.get(video.video_id, {})
            enriched_video = video.model_copy(
                update={
                    "view_count": int(stats["viewCount"])
                    if "viewCount" in stats
                    else None,
                    "like_count": int(stats["likeCount"])
                    if "likeCount" in stats
                    else None,
                    "comment_count": int(stats["commentCount"])
                    if "commentCount" in stats
                    else None,
                }
            )
            enriched_videos.append(enriched_video)

        return enriched_videos

youtube_client = YouTubeClient(settings.YOUTUBE_API_KEY)
from apify_client import ApifyClient
from typing import Any, Dict, List, Iterator

from trend_bot.config import settings
from trend_bot.logger import setup_logger

logger = setup_logger("client_logger")

class InstagramClient:
    """Client for extracting posts, reels, and their embedded music metadata via Apify."""
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.client = ApifyClient(self.api_key)

    def scrape_trends_with_audio(
        self, 
        targets: List[str], 
        posts_limit: int = 15, 
        publish_after: str | None = None
    ) -> List[Dict[str, Any]]:
        actor_id = "apify/instagram-scraper"
        
        target_urls = [f"https://www.instagram.com/explore/tags/{target.strip('')}/" for target in targets]
        
        run_input: dict[str, Any] = {
            "directUrls": target_urls,
            "resultsLimit": posts_limit,
            "addParentData": False,
        }

        if publish_after:
            run_input["onlyPostsNewerThan"] = publish_after

        run = self.client.actor(actor_id).call(run_input=run_input)
        if not run:
            logger.error("Apify actor run failed.")
            raise RuntimeError("Apify actor run failed.")

        dataset_id = getattr(run, "default_dataset_id", None)
        if not dataset_id:
            logger.error("Could not retrieve default dataset ID.")
            raise RuntimeError("Could not retrieve default dataset ID.")

        items: Iterator[dict[Any, Any]] = self.client.dataset(dataset_id).iterate_items() #type: ignore

        parsed_data: list[dict[str, Any]] = []
        for item in items:
            # Extract the embedded music/audio info if present on the Reel/Post
            music_info: Any = item.get("musicInfo") or item.get("audioData") or {}
            
            parsed_data.append({
                "post_id": item.get("id"),
                "caption": item.get("caption"),
                "media_type": item.get("type"),
                "timestamp": item.get("timestamp"),
                "likes": item.get("likesCount", 0),
                "comments": item.get("commentsCount", 0),
                "link": item.get("url"),
                # Audio metadata extracted straight from high-performing posts
                "track_title": music_info.get("songName") or music_info.get("title") or "Original Audio",
                "artist": music_info.get("artistName") or music_info.get("artist") or "Unknown Artist",
                "audio_url": music_info.get("url")
            })
        return parsed_data

instagram_client = InstagramClient(settings.APIFY_INSTAGRAM_TOKEN)
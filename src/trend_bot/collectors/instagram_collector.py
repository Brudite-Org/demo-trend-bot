from typing import Any, Dict, List
from sqlalchemy.orm import Session

from trend_bot.clients.client_instagram import instagram_client
from trend_bot.database.database import InstagramModel
from trend_bot.logger import setup_logger

logger = setup_logger("instagram_collector")

class InstagramCollector:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.client = instagram_client

    def collect(
        self, 
        targets: List[str], 
        posts_limit: int = 10, 
        top_n: int = 10,
        publish_after: str | None = None
    ) -> List[Dict[str, Any]]:
        try:
            raw_posts = self.client.scrape_trends_with_audio(
                targets, 
                posts_limit=posts_limit, 
                publish_after=publish_after
            )
            sorted_posts = sorted(
                raw_posts, 
                key=lambda p: (p.get("likes", 0) + p.get("comments", 0)), 
                reverse=True
            )
            return sorted_posts[:top_n]
        except Exception as e:
            logger.error(f"Failed to fetch intelligence via Apify: {e}")
            return []

    def save_to_db(self, db: Session, posts: List[Dict[str, Any]]) -> None:
        """Persists collected Instagram payloads into the database."""
        added_count = 0
        updated_count = 0
        for post in posts:
            post_id = post.get("post_id")
            if not post_id:
                continue
            fields = [
                "caption", "media_type", "timestamp", "link", 
                "track_title", "artist", "audio_url"
            ]
            existing_post = db.query(InstagramModel).filter(InstagramModel.post_id == post_id).first()
            if existing_post:
                # Fields that can be directly mapped via loop
                for field in fields:
                    if field in post:
                        setattr(existing_post, field, post.get(field))
                        
                # Handling fields that requires a default fallback value explicitly
                existing_post.likes = post.get("likes", 0)
                existing_post.comments = post.get("comments", 0)
                updated_count += 1
            else:
                db_post = InstagramModel(
                    **{
                        field: post.get(field, 0) if field in ["likes", "comments"]
                        else post.get(field)
                        for field in ["post_id"] + fields + ["likes","comments"]
                    }
                )
                db.add(db_post)
                added_count += 1
        db.commit()
        logger.info(f"Committed Instagram data to db. ({added_count} added, {updated_count} updated)")

    def format_summary(self, posts: List[Dict[str, Any]]) -> str:
        lines = ["[Top Market Content & Associated Audio Intelligence]"]
        for i, post in enumerate(posts, 1):
            caption_text = post.get('caption') or 'No caption'
            lines.append(
                f"\n{i}. Post Content: \"{caption_text[:100]}...\"\n"
                f"   - Engagement:   {post.get('likes')} likes, {post.get('comments')} comments\n"
                f"   - Attached Audio: \"{post.get('track_title')}\" by {post.get('artist')}\n"
                f"   - URL: {post.get('link')}"
            )
        return "\n".join(lines)
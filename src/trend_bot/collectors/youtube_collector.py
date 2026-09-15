from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Any, Dict, List

from trend_bot.clients.client_youtube import youtube_client
from trend_bot.database.database import VideoModel
from trend_bot.logger import setup_logger
from trend_bot.utils.constants import all_fields, update_fields

logger = setup_logger("youtube_collector")

class YouTubeCollector:
    """Collects, normalizes, manages persistence, and computes analytics for YouTube video trends."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.client = youtube_client

    def collect(self, query: str | List[str], max_results: int = 5) -> List[Dict[str, Any]]:
        """Searches and enriches YouTube videos, returning structured dictionaries."""
        try:
            video_objs = self.client.search_videos(
                query=query,
                max_results=max_results
            )

            videos_data: list[dict[str, Any]] = []

            for v in video_objs:
                video_data = {field: getattr(v, field) for field in all_fields}

                if hasattr(video_data["published_at"], "isoformat"):
                    video_data["published_at"] = video_data["published_at"].isoformat()
                else:
                    video_data["published_at"] = str(video_data["published_at"])

                videos_data.append(video_data)
            return videos_data
        except Exception as e:
            logger.error(f"Failed to fetch YouTube intelligence: {e}")
            return []

    def save_to_db(self, db: Session, videos: List[Dict[str, Any]]) -> None:
        """Persists collected video payloads into PostgreSQL/SQLite."""

        added_count = 0
        updated_count = 0

        for video in videos:
            vid_id = video.get("video_id")
            existing_video = (db.query(VideoModel).filter(VideoModel.video_id == vid_id).first())

            if existing_video:
                # Update existing record dynamically
                for field in update_fields:
                    setattr(existing_video, field, video.get(field))
                updated_count += 1

            else:
                # Create new record dynamically
                db_video = VideoModel(**{field: video.get(field) for field in all_fields})
                db.add(db_video)
                added_count += 1
                logger.info(f"Added: {video.get('title')}")
        db.commit()
        logger.info(f"Committed to db.({added_count} added, {updated_count} updated)")

    def get_video_analytics(self, db: Session) -> dict[str, Any]:
        """Calculates overall metrics and trend summaries from the stored videos[cite: 1]."""
        total_videos = db.query(VideoModel).count()
        if total_videos == 0:
            return {"total_videos": 0}
        
        aggregates = db.query(
            func.sum(VideoModel.view_count).label("total_views"),
            func.avg(VideoModel.view_count).label("avg_views"),
            func.sum(VideoModel.like_count).label("total_likes"),
            func.avg(VideoModel.like_count).label("avg_likes"),
            func.sum(VideoModel.comment_count).label("total_comments"),
            func.avg(VideoModel.comment_count).label("avg_comments"),
        ).first()
        
        top_video = db.query(VideoModel).order_by(VideoModel.view_count.desc()).first()
        
        return {
            "total_videos": total_videos,
            "total_views": aggregates.total_views or 0,
            "avg_views": round(aggregates.avg_views or 0, 2),
            "total_likes": aggregates.total_likes or 0,
            "avg_likes": round(aggregates.avg_likes or 0, 2),
            "total_comments": aggregates.total_comments or 0,
            "avg_comments": round(aggregates.avg_comments or 0, 2),
            "top_video_title": top_video.title if top_video else None,
            "top_video_views": top_video.view_count if top_video else 0,
        }

    def format_summary(self, videos: List[Dict[str, Any]]) -> str:
        """Converts structured YouTube video data into a text block for Gemini."""
        lines = ["[Youtube Content]"]
        for i, video in enumerate(videos, 1):
            title = video.get("title", "Untitled")
            description = video.get("description", "")
            channel = video.get("channel_title", "Unknown Channel")
            vid_id = video.get("video_id")
            video_url = f"https://www.youtube.com/watch?v={vid_id}" if vid_id else "N/A"
            lines.append(
                f"{i}. YouTube Video: \"{title}\" by {channel}\n"
                f"   - Description: {description[:100]}...\n"
                f"   - URL: {video_url}"
            )
        return "\n".join(lines)
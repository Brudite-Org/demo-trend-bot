from typing import Any, Dict, List
from sqlalchemy import func
from sqlalchemy.orm import Session
from trend_bot.clients.client_youtube import YouTubeClient
from trend_bot.database.database import VideoModel

class YouTubeCollector:
    """Collects, normalizes, manages persistence, and computes analytics for YouTube video trends."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.client = YouTubeClient(api_key=self.api_key)

    def collect(self, query: str | List[str], max_results: int = 5) -> List[Dict[str, Any]]:
        """Searches and enriches YouTube videos, returning structured dictionaries."""
        try:
            video_objs = self.client.search_videos(query=query, max_results=max_results)
            videos_data = []
            for v in video_objs:
                videos_data.append({
                    "video_id": v.video_id,
                    "title": v.title,
                    "description": v.description,
                    "channel_id": v.channel_id,
                    "channel_title": v.channel_title,
                    "published_at": v.published_at.isoformat() if hasattr(v.published_at, "isoformat") else str(v.published_at),
                    "view_count": v.view_count,
                    "like_count": v.like_count,
                    "comment_count": v.comment_count,
                })
            return videos_data
        except Exception as e:
            print(f"Failed to fetch YouTube intelligence: {e}")
            return []

    def save_to_db(self, db: Session, videos: List[Dict[str, Any]]) -> None:
        """Persists collected video payloads into PostgreSQL/SQLite."""
        added_count = 0
        updated_count = 0
        for video in videos:
            vid_id = video.get("video_id")
            existing_video = db.query(VideoModel).filter(VideoModel.video_id == vid_id).first()
            if existing_video:
                existing_video.title = video.get("title")
                existing_video.description = video.get("description")
                existing_video.channel_title = video.get("channel_title")
                existing_video.view_count = video.get("view_count")
                existing_video.like_count = video.get("like_count")
                existing_video.comment_count = video.get("comment_count")
                updated_count += 1
            else:
                db_video = VideoModel(
                    video_id=vid_id,
                    title=video.get("title"),
                    description=video.get("description"),
                    channel_id=video.get("channel_id"),
                    channel_title=video.get("channel_title"),
                    published_at=video.get("published_at"),
                    view_count=video.get("view_count"),
                    like_count=video.get("like_count"),
                    comment_count=video.get("comment_count"),
                )
                db.add(db_video)
                added_count += 1
                print(f"Added: {video.get('title')}")
        db.commit()
        print(f"Committed to db. ({added_count} added, {updated_count} updated)")

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
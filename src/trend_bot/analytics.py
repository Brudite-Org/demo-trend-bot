from sqlalchemy.orm import Session
from sqlalchemy import func
from trend_bot.database import VideoModel
from typing import Any


def get_video_analytics(db: Session) -> dict[str, Any]:
    """Calculates overall metrics and trend summaries from the stored videos."""
    total_videos = db.query(VideoModel).count()
    if total_videos == 0:
        return {"total_videos": 0}

    # Aggregate totals and averages
    aggregates = db.query(
        func.sum(VideoModel.view_count).label("total_views"),
        func.avg(VideoModel.view_count).label("avg_views"),
        func.sum(VideoModel.like_count).label("total_likes"),
        func.avg(VideoModel.like_count).label("avg_likes"),
        func.sum(VideoModel.comment_count).label("total_comments"),
        func.avg(VideoModel.comment_count).label("avg_comments"),
    ).first()

    # Find top video by views
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
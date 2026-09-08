from sqlalchemy.orm import Session
from trend_bot.database import VideoModel, engine
from trend_bot.models import Video
from trend_bot import database

def init_db():
    database.Base.metadata.create_all(bind=engine)

def save_videos_to_db(db: Session, videos: list[Video]):

    added_count = 0
    updated_count = 0

    for video in videos:
        # Check if this video already exists in the database
        existing_video = db.query(VideoModel).filter(VideoModel.video_id == video.video_id).first()

        if existing_video:
            existing_video.title = video.title
            existing_video.description = video.description
            existing_video.channel_title = video.channel_title
            existing_video.view_count = video.view_count
            existing_video.like_count = video.like_count
            existing_video.comment_count = video.comment_count
            updated_count += 1

        else:
            db_video = VideoModel(
                video_id=video.video_id,
                title=video.title,
                description=video.description,
                channel_id=video.channel_id,
                channel_title=video.channel_title,
                published_at=video.published_at,
                view_count=video.view_count,
                like_count=video.like_count,
                comment_count=video.comment_count,
            )
            db.add(db_video)
            added_count += 1
            print(f"Added: {video.title}")

    db.commit()
    print(f"Committed to db. ({added_count} added, {updated_count} updated)")
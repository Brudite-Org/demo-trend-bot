from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, String, Integer, JSON, DateTime
from trend_bot.config import settings
from datetime import datetime, timezone


url = settings.DATABASE_URL
engine=create_engine(url)
sessionLocal = sessionmaker(bind=engine, autocommit=False)

Base = declarative_base()

class VideoModel(Base):
    __tablename__ = "videos"

    video_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    channel_id = Column(String, nullable=False)
    channel_title = Column(String, nullable=False)
    published_at = Column(String, nullable=False)
    view_count = Column(Integer, nullable=True)
    like_count = Column(Integer, nullable=True)
    comment_count = Column(Integer, nullable=True)

class GoogleTrendsModel(Base):
    __tablename__ = "google_trends_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String, index=True)
    geo = Column(String, default="IN")
    date_range = Column(String, default="now 7-d")
    
    related_queries = Column(JSON, nullable=True)
    related_topics = Column(JSON, nullable=True)
    interest_over_time = Column(JSON, nullable=True)
    
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class InstagramModel(Base):
    __tablename__ = "instagram_posts"
    
    post_id = Column(String, primary_key=True, index=True)
    caption = Column(String, nullable=True)
    media_type = Column(String, nullable=True)
    timestamp = Column(String, nullable=True)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    link = Column(String, nullable=True)
    track_title = Column(String, nullable=True)
    artist = Column(String, nullable=True)
    audio_url = Column(String, nullable=True)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
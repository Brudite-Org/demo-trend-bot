from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, String, Integer
from trend_bot.config import settings

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


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
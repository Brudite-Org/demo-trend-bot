from datetime import datetime

from pydantic import BaseModel
    
class Video(BaseModel):
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: datetime

    view_count: int | None = None
    like_count: int | None = None
    comment_count: int | None = None
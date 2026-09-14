from typing import Any, Dict, List
from trend_bot.clients.client_instagram import InstagramClient

class InstagramCollector:
    def __init__(self, api_key: str | None = None):
        self.client = InstagramClient(api_key=api_key)

    def collect(
        self, 
        targets: List[str],
        posts_limit: int = 10, 
        top_n: int = 10,
        publish_after: str | None = None
    ) -> list[dict[str, Any]]:
        try:
            raw_posts = self.client.scrape_trends_with_audio(
                targets, 
                posts_limit=posts_limit, 
                publish_after=publish_after
            )
            
            # Sort by total engagement to surface the tracks used by top-performing content
            sorted_posts: list = sorted(
                raw_posts, 
                key=lambda p: (p.get("likes", 0) + p.get("comments", 0)), 
                reverse=True
            )
            
            return sorted_posts[:top_n]
        
        except Exception as e:
            print(f"Failed to fetch intelligence via Apify: {e}")
            return []

    def format_summary(self, posts: List[Dict[str, Any]]) -> str:
        lines = ["[Top Market Content & Associated Audio Intelligence]"]
        for i, post in enumerate(posts, 1):
            caption_text = post.get('caption') or 'No caption'
            lines.append(
                f"\n{i}. Post Content: \"{caption_text[:100]}...\"\n"
                f"   - Engagement: 🚀 {post.get('likes')} likes, {post.get('comments')} comments\n"
                f"   - 🎵 Attached Audio: \"{post.get('track_title')}\" by {post.get('artist')}\n"
                f"   - URL: {post.get('link')}"
            )
        return "\n".join(lines)
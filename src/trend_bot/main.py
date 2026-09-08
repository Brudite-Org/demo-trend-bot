from trend_bot.client_youtube import YouTubeClient
from trend_bot.db_opretaions import init_db, save_videos_to_db
from trend_bot.database import sessionLocal
from trend_bot.analytics import get_video_analytics
from trend_bot.ai_analysis import run_trend_analyst_agent
from trend_bot.discord_dispatcher import send_to_discord
from trend_bot.config import settings

def main():

    init_db()

    keywords = ["talent acquisition", "hr tech"]
    client = YouTubeClient(api_key=settings.YOUTUBE_API_KEY)
    videos = client.search_videos(query=keywords, max_results=5)

    print(f"Fetched {len(videos)} from API.")

    db = sessionLocal()
    try:
        save_videos_to_db(db, videos)

        stats = get_video_analytics(db)
        
        print(f"Total Videos Analyzed: {stats['total_videos']}")
        print(f"Total Views: {stats['total_views']:,} (Avg: {stats['avg_views']:,})")
        print(f"Total Likes: {stats['total_likes']:,} (Avg: {stats['avg_likes']:,})")
        print(f"Total Comments: {stats['total_comments']:,} (Avg: {stats['avg_comments']:,})")
        
        if stats['top_video_title']:
            print(f"\nTop Trending Video: '{stats['top_video_title']}' ({stats['top_video_views']:,} views)")

        formatted_trends: list[str] = []
        for i, video in enumerate(videos, 1):
            title = getattr(video, "title", "Untitled")
            description = getattr(video, "description", "")
            channel = getattr(video, "channel_title", "Unknown Channel")
            vid_id = getattr(video, "video_id", None)
            video_url = f"https://www.youtube.com/watch?v={vid_id}" if vid_id else "N/A"

            formatted_trends.append(
                f"{i}. YouTube Video: \"{title}\" by {channel}\n"
                f"   - Description: {description}...\n"
                f"   - URL: {video_url}"
            )

        trending_data_payload = "\n".join(formatted_trends)

        print("\nGenerating SkillBrew Social Media Trend Intelligence Digest...")
        discord_digest = run_trend_analyst_agent(trending_data_payload)
        
        print("\n" + "="*60)
        print("📢 SKILLBREW SOCIAL MEDIA TREND DIGEST (DISCORD READY)")
        print("="*60)
        print(discord_digest)
        print("="*60)

        send_to_discord(discord_digest)
    finally:
        db.close()
    print("saved")

if __name__ == "__main__":
    main()
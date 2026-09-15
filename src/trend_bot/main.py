from trend_bot.ai_analysis import run_trend_analyst_agent
from trend_bot.collectors.instagram_collector import InstagramCollector
from trend_bot.collectors.google_trends_collector import GoogleTrendsCollector
from trend_bot.collectors.youtube_collector import YouTubeCollector
from trend_bot.config import settings
from trend_bot.database.database import init_db, get_db
from trend_bot.discord_dispatcher import send_to_discord
from trend_bot.logger import setup_logger
from trend_bot.utils.constants import google_keywords, youtube_keywords, target_tags

logger = setup_logger("main")
    
def main():

    init_db()

    ##Youtube
    logger.info("Fetching from Youtube......")
    youtube_collector = YouTubeCollector(api_key=settings.YOUTUBE_API_KEY if settings.YOUTUBE_API_KEY else "NO YOUTUBE API KEY")
    videos = youtube_collector.collect(query=youtube_keywords, max_results=5)

    ##Google Trends
    logger.info("Fetching from Google Trends.....")
    google_trends_collector = GoogleTrendsCollector(api_key=settings.SERPAPI_KEY if settings.SERPAPI_KEY else "NO SERP API KEY")
    trends_results = google_trends_collector.collect(google_keywords)

    #Instagram
    logger.info("Fetching from Instagram......")
    instagram_collector = InstagramCollector(api_key=settings.APIFY_INSTAGRAM_TOKEN if settings.APIFY_INSTAGRAM_TOKEN else "NO INSTAGRAM TOKEN")
    ig_posts = instagram_collector.collect(target_tags, posts_limit=100, top_n=5, publish_after="2026-09-01")

    with next(get_db()) as db:
        
        youtube_collector.save_to_db(db, videos)
        google_trends_collector.save_to_db(db, trends_results)
        instagram_collector.save_to_db(db, ig_posts)

        youtube_summary = youtube_collector.format_summary(videos)
        google_trends_summary = google_trends_collector.format_summary(trends_results)
        instagram_summary = instagram_collector.format_summary(ig_posts)
        
        trending_data_payload = f"""
        {youtube_summary}
        [Google Trends Data]
        {google_trends_summary}
        [Instagram data]
        {instagram_summary}
        """

        logger.info("\nGenerating SkillBrew Social Media Trend Intelligence Digest...")
        discord_digest = run_trend_analyst_agent(trending_data_payload)
        send_to_discord(discord_digest)

    logger.info("saved")

if __name__ == "__main__":
    main()
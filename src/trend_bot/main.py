from trend_bot.collectors.google_trends_collector import GoogleTrendsCollector
from trend_bot.collectors.youtube_collector import YouTubeCollector
from trend_bot.database.database import sessionLocal
from trend_bot.ai_analysis import run_trend_analyst_agent
from trend_bot.discord_dispatcher import send_to_discord
from trend_bot.config import settings
from trend_bot.collectors.instagram_collector import InstagramCollector
from trend_bot.database.database import init_db 


def main():

    init_db()

    google_keywords = [
    "talent assessment",
    "skill assessment",
    "HR technology",
    "talent acquisition",
    "recruiting software",
    "candidate experience",
    "skills-based hiring",
    "pre-employment testing",
    "employee assessment",
    "hiring software",
    "tech hiring",
    "engineering hiring",
    "technical hiring",
    "recruiter productivity",
    "human resources software",
    "HR analytics",
    "workforce technology",
    "remote hiring",
    "gig economy hiring",
    "diversity hiring",
    "employer branding",
    ]


    youtube_keywords = [
    "talent assessment", "skills-based hiring", "AI recruiting",
    "candidate experience", "HR technology", "pre-employment testing",
    "technical interview", "engineering hiring", "tech hiring 2026",
    "workforce assessment", "employee skills", "hiring software","recruiter tips", "interview hack", "hiring mistake", "resume tips",
    "job search", "career advice", "HR tip", "work hack", "salary negotiation",
    "behavioral interview", "STAR method", "LinkedIn profile",
    "skills assessment", "candidate red flag", "job offer",
    ]

    target_tags = ["FutureOfWork", "TalentAcquisition", "hiringtrends", "recruitmentautomation"]

    ##Youtube
    print("Fetching from Youtube......")
    youtube_collector = YouTubeCollector(api_key=settings.YOUTUBE_API_KEY if settings.YOUTUBE_API_KEY else "NO YOUTUBE API KEY")
    videos = youtube_collector.collect(query=youtube_keywords, max_results=5)

    ##Google Trends
    print("Fetching from Google Trends.....")
    # google_trends_collector = GoogleTrendsCollector(api_key=settings.SERPAPI_KEY if settings.SERPAPI_KEY else "NO SERP API KEY")
    # trends_results = google_trends_collector.collect(google_keywords)

    #Instagram
    # print("Fetching from Instagram......")
    # instagram_collector = InstagramCollector(api_key=settings.APIFY_INSTAGRAM_TOKEN if settings.APIFY_INSTAGRAM_TOKEN else "NO INSTAGRAM TOKEN")
    # ig_posts = instagram_collector.collect(target_tags, posts_limit=100, top_n=5, publish_after="2026-09-01")
    # instagram_summary = instagram_collector.format_summary(ig_posts)

    db = sessionLocal()
    try:
        youtube_collector.save_to_db(db, videos)
        # google_trends_collector.save_to_db(db, trends_results)

        youtube_summary = youtube_collector.format_summary(videos)
        # google_trends_summary = google_trends_collector.format_summary(trends_results)
        
        trending_data_payload = f"""
        {youtube_summary}"""
        # [Google Trends Data]
        # {google_trends_summary}
        # [Instagram data]
        # {instagram_summary}
        # """

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
import schedule
from trend_bot.main import main
import time

def job():
    print("\n⏰ Scheduled job triggered: Running SkillBrew Trend Intelligence Pipeline...")
    try:
        main()
        print("✅ Scheduled digest successfully processed and sent to Discord.")
    except Exception as e:
        print(f"❌ Error during scheduled pipeline run: {e}")


def start_scheduler():
    # Option A: Run every day at a specific time (e.g., 9:00 AM)
    # schedule.every().day.at("09:00").do(job)

    # Option B: For quick testing right now, you can uncomment this to test every 30 seconds:
    schedule.every(5).seconds.do(job)

    print("🤖 SkillBrew Scheduler is active. Waiting for scheduled time...")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    start_scheduler()
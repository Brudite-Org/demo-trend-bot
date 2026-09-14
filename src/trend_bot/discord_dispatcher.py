import requests
from trend_bot.config import settings

def send_to_discord(content: str) -> bool:
    """Sends the formatted trend digest to a Discord channel via webhook."""
    webhook_url = settings.DISCORD_WEBHOOK_URL
    
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL is not set in environment variables.")
        return False

    # Discord has a 2000 character limit per message. 
    # If your digest is longer, we can split it or truncate safely.
    print(len(content))
    if len(content) <= 1900:
        payloads = [{"content": content}]
    else:
        payloads: list[dict[str, str]] = []
        for i in range(0, len(content), 1900):
            content_chunk = content[i:i+1900]
            payloads.append({"content": content_chunk})

    try:
        for payload in payloads:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
        print("Successfully sent trend digest to Discord!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send message to Discord: {e}")
        return False
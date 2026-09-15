import requests

from trend_bot.config import settings
from trend_bot.logger import setup_logger

logger = setup_logger("discord_dispatcher")

def send_to_discord(content: str) -> bool:
    """Sends the formatted trend digest to a Discord channel via webhook."""
    webhook_url = settings.DISCORD_WEBHOOK_URL
    
    if not webhook_url:
        logger.warning("DISCORD_WEBHOOK_URL is not set in environment variables.")
        return False

    # Discord has a 2000 character limit per message. 
    # If the digest is longer, we split it and send in parts.
    logger.info(f"Preparing to send digest of {len(content)} characters")
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
        logger.info("Successfully sent trend digest to Discord!")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to send message to Discord: {e}")
        return False
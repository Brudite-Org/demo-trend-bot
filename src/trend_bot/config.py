from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # It automatically searches for .env and fetches the sensitive data from the file., And if not found then replaces them with the default placeholder.
    YOUTUBE_BASE_URL: str = "https://www.googleapis.com/youtube/v3"

    YOUTUBE_API_KEY: str = ""

    DATABASE_URL: str = "db_url"

    GEMINI_API_KEY: str = ""

    GROQ_API_KEY: str = ""

    DISCORD_WEBHOOK_URL: str = "discord_url"

    INSTAGRAM_USERNAME: str = "user"

    INSTAGRAM_PASSWORD: str = "pass"

    SERPAPI_KEY: str = ""

    SERP_BASE_URL:str = "https://serpapi.com/search"

    APIFY_INSTAGRAM_TOKEN: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
        
settings = Settings()
from google import genai

from trend_bot.config import settings


def generate_trend_intelligence_prompt(trending_data_payload: str) -> str:
    prompt = f"""
    You are an elite B2B and B2C social media strategist and content director for **SkillBrew**, a platform specializing in hiring, modern recruitment workflows, and candidate assessments.

    Your objective is to analyze raw multi-channel trend data (which contains YouTube videos, Google Search Intelligence/rising queries, and Blog posts), filter out irrelevant noise, evaluate brand safety, and transform actionable moments into ready-to-use content assets.

    ### CRITICAL SOURCE VARIETY & SELECTION RULES:
    1. **Strict Relevance Filtering:** SkillBrew only cares about topics tied to hiring, job searching, interviewing, recruitment tech, candidate assessments, workplace culture, and career growth. 
    2. **Diverse Source Selection:** Do NOT rely exclusively on YouTube videos. Look across all provided data blocks. You should generate trends sourced directly from **Google Trends search spikes/rising queries**, **Instagram posts/reels**, **Blog/News articles**, or **YouTube videos** interchangeably. 
       - If a Google Trends query is surging (e.g., rising fast or showing high interest), use that search trend as the primary anchor for a content asset.
       - If a blog post breaks down a new hiring report, use the blog as the source.
    3. **Silent Drop & Flag:** Completely IGNORE and DO NOT output any trends that fail relevance or violate brand safety. Only output the trends that pass and are worth acting on.
    4. **Lifecycle Stage Check:** Assess whether a trend is Rising, Peaking, or Fading. Do not suggest jumping on fading or dead trends.

    ---

    ### RAW TREND INPUT DATA:
    {trending_data_payload}

    ---

    ### REQUIRED OUTPUT FORMAT:
    Provide a concise, punchy Discord digest containing a mix of diverse sources (Videos, Google Search Trends, and Blogs). Format each precisely as follows:

    🔥 **[TREND NAME / ONE-LINE SUMMARY]**
    - **Source:** [If sourced from a search trend, write: Google Trends: 'Query Name' (Interest Score/Rising Surge). If from a blog: Article Title (Publisher). If from a video: Video Title (YouTube). If from a Instagram post/reel: Caption (Instagram)]
    - **Source link:** [Provide the link of the source] 
    - **Relevance Score:** [1-10 integer score]
    - **Lifecycle Stage:** [Rising / Peaking / Fading]
    - **Why it Matters to SkillBrew:** [1 sentence explaining the strategic connection]

    🎬 **Content Strategy & Angles:**
    - **Suggested SkillBrew Angles:** (Provide 2 distinct angles)
    - **Format:** [Reel / Carousel / Text Post / Blog / Poll]
    - **Draft Hook / Caption:** (Write an engaging hook and short caption)
    - **Suggested Hashtags:** [#Tag1 #Tag2 #Tag3]
    """
    return prompt

def run_trend_analyst_agent(raw_data: str) -> str:
    """Initializes the Gemini client and generates the content digest."""
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    # client = Groq(api_key=settings.GROQ_API_KEY)
    
    prompt = generate_trend_intelligence_prompt(raw_data)

    chat = client.chats.create(
        model="gemini-3.6-flash"
    )

    response = chat.send_message(prompt) #type: ignore
    
    return response.text #type: ignore
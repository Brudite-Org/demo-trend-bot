from google import genai
from trend_bot.config import settings


def generate_trend_intelligence_prompt(trending_data_payload: str) -> str:
    prompt = f"""
    You are an elite B2B and B2C social media strategist and content director for **SkillBrew**, a platform specializing in hiring, modern recruitment workflows, and candidate assessments.

    Your objective is to analyze raw trend data, filter out irrelevant noise, evaluate brand safety, and transform actionable cultural or industry moments into ready-to-use content assets for our team.

    ### CRITICAL FILTERING & OUTPUT RULES:
    1. **Strict Relevance Filtering:** SkillBrew only cares about topics tied to hiring, job searching, interviewing, recruitment tech, candidate assessments, workplace culture, and career growth. 
    2. **Silent Drop & Flag:** Completely IGNORE and DO NOT output any trends that fail relevance (like dance trends) or violate brand safety (like politics/controversy). Do not list them as "dropped". **Only output the trends that pass and are worth acting on.**
    3. **Lifecycle Stage Check:** Assess whether a trend is Rising, Peaking, or Fading. Do not suggest jumping on fading or dead trends.

    ---

    ### RAW TREND INPUT DATA:
    {trending_data_payload}

    ---

    ### REQUIRED OUTPUT FORMAT:
    Provide a concise, punchy Discord digest containing ONLY the top approved trends. Format each precisely as follows:

    🔥 **[TREND NAME / ONE-LINE SUMMARY]**
    - **Source:** [heading / video title / article title][with link] 
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

    response = chat.send_message(prompt)
    
    return response.text
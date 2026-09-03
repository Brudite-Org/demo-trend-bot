import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any


def fetch_google_trends(geo: str = "US", category: int = 18, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Fetches real-time search trends from the public Google Trends RSS feed.
    geo options: 'US', 'IN', 'GB', etc.
    """
    url = f"https://trends.google.com/trending/rss?geo={geo}&category={category}&sort=search-volume"
    results = []
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            print(root)
            # print(root.findall("./channel/item"))
            for item in root.findall("./channel/item")[:limit]:
                print(item)
                title = item.findtext("title")
                approx_traffic = item.findtext("{https://trends.google.com/trending/rss}approx_traffic") or "N/A"
                news_items = item.findall("{https://trends.google.com/trending/rss}news_item")
                
                context = ""
                if news_items:
                    snippet_title = news_items[0].findtext("{https://trends.google.com/trending/rss}news_item_title")
                    snippet_url = news_items[0].findtext("{https://trends.google.com/trending/rss}news_item_url")
                    context = f"Headline: {snippet_title} ({snippet_url})"
                
                results.append({
                    "trend_name": title,
                    "source": f"Google Trends ({geo})",
                    "traffic": approx_traffic,
                    "raw_text": context
                })
        else:
            print(f"Google Trends returned status {response.status_code}")
    except Exception as e:
        print(f"Google Trends fetch error: {e}")

    return results


if __name__ == "__main__":
    print("\n Searching googrl trends")
    gtrends_data = fetch_google_trends(geo="IN", category=18, limit=5)
    for trend in gtrends_data:
        print(f"• [{trend['source']}] {trend['trend_name']} (Traffic: {trend.get('traffic')})")
    
    print("Data Scraped")
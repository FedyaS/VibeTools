import feedparser
from time import sleep
import time
import json

# Load seen_articles
try:
    with open('seen_articles.json', 'r') as f:
        seen_articles = json.load(f)
except:
    seen_articles = {}

# List of RSS feeds
feeds = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "http://rss.cnn.com/rss/cnn_latest.rss",
    "https://www.reuters.com/arc/outboundfeeds/newsroom/?format=rss",
    "https://www.theguardian.com/world/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://feeds.feedburner.com/TechCrunch/",
]

while True:
    try:
        for feed_url in feeds:
            feed = feedparser.parse(feed_url)
            feed_title = feed.feed.get('title', 'Unknown')
            for entry in feed.entries:
                # Use article ID or link as unique identifier
                article_id = entry.get('id', entry.get('link', ''))
                # Use published time as fallback for uniqueness
                pub_time = entry.get('published_parsed', time.gmtime())
                pub_timestamp = time.mktime(pub_time) if pub_time else time.time()
                
                # Check if article is new
                if article_id not in seen_articles or seen_articles[article_id] < pub_timestamp:
                    print(f"{feed_title}: {entry.title} - {entry.link}")
                    # Do something here (e.g., send email, notification, etc.)
                    seen_articles[article_id] = pub_timestamp
        with open('seen_articles.json', 'w') as f:
            json.dump(seen_articles, f)
    except Exception as e:
        print(f"Error: {e}")
    sleep(30)  # Check every 30 seconds
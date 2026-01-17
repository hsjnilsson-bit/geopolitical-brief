import os
import requests
import feedparser
from datetime import datetime, timedelta
import pytz
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import time
import schedule

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
RECIPIENT_EMAIL = 'hsjnilsson@gmail.com'
SENDER_EMAIL = 'worldbrief@geopolitical-intel.com'

RSS_FEEDS = {
    'The Economist': 'https://www.economist.com/rss',
    'Reuters World': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
    'AP News': 'https://apnews.com/apf-topnews',
    'ISW': 'https://www.understandingwar.org/rss.xml',
    'Defense One': 'https://www.defenseone.com/rss/',
    'Foreign Policy': 'https://foreignpolicy.com/feed/',
    'War on the Rocks': 'https://warontherocks.com/feed/',
}
def fetch_news():
    all_articles = []
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                article = {
                    'source': source_name,
                    'title': entry.get('title', 'No title'),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:200] + '...' if entry.get('summary') else ''
                }
                all_articles.append(article)
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")
            continue
    return all_articles

def categorize_articles(articles):
    categories = {
        'Military & Security': [],
        'Economy & Energy': [],
        'Diplomacy & Politics': [],
        'Technology & Cyber': [],
        'Other': []
    }
    military_keywords = ['military', 'war', 'defense', 'army', 'navy', 'conflict', 'weapon', 'security', 'terror']
    economy_keywords = ['economy', 'energy', 'oil', 'gas', 'trade', 'market', 'sanction', 'dollar', 'euro']
    diplomacy_keywords = ['diplomacy', 'treaty', 'summit', 'election', 'government', 'minister', 'president']
    tech_keywords = ['cyber', 'technology', 'AI', 'chip', 'semiconductor', 'hack', 'digital']
    for article in articles:
        text = (article['title'] + ' ' + article['summary']).lower()
        if any(keyword in text for keyword in military_keywords):
            categories['Military & Security'].append(article)
        elif any(keyword in text for keyword in economy_keywords):
            categories['Economy & Energy'].append(article)
        elif any(keyword in text for keyword in diplomacy_keywords):
            categories['Diplomacy & Politics'].append(article)
        elif any(keyword in text for keyword in tech_keywords):
            categories['Technology & Cyber'].append(article)
        else:
            categories['Other'].append(article)
    return categories
def generate_html_report(categories):
    stockholm_tz = pytz.timezone('Europe/Stockholm')
    current_time = datetime.now(stockholm_tz)
    html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{font-family:Georgia,serif;max-width:700px;margin:0 auto;padding:20px;background-color:#f5f5f5;color:#333}.header{background-color:#1a1a1a;color:#fff;padding:30px;text-align:center;border-radius:8px 8px 0 0}.header h1{margin:0;font-size:28px;font-weight:300;letter-spacing:2px}.date{color:#999;font-size:14px;margin-top:10px}.content{background-color:#fff;padding:30px;border-radius:0 0 8px 8px}.category{margin-bottom:35px}.category-title{font-size:20px;color:#1a1a1a;border-bottom:2px solid #e0e0e0;padding-bottom:10px;margin-bottom:20​​​​​​​​​​​​​​​​
def send_email(html_content):
    try:
        message = Mail(
            from_email=Email(SENDER_EMAIL),
            to_emails=To(RECIPIENT_EMAIL),
            subject=f'Geopolitical Brief - {datetime.now(pytz.timezone("Europe/Stockholm")).strftime("%B %d, %Y")}',
            html_content=Content("text/html", html_content)
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent! Status code: {response.status_code}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def generate_and_send_brief():
    print(f"Generating brief at {datetime.now(pytz.timezone('Europe/Stockholm'))}")
    articles = fetch_news()
    print(f"Fetched {len(articles)} articles")
    categories = categorize_articles(articles)
    html_report = generate_html_report(categories)
    send_email(html_report)
    print("Brief sent successfully!")

def run_scheduler():
    schedule.every().day.at("05:00").do(generate_and_send_brief)
    print("Scheduler started.​​​​​​​​​​​​​​​​

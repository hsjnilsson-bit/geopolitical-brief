import os
import requests
import feedparser
from datetime import datetime, timedelta
import pytz
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import schedule

RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = 'onboarding@resend.dev'
RECIPIENT_EMAIL = 'hsjnilsson@gmail.com'

RSS_FEEDS = {
    'The Economist': 'https://www.economist.com/rss',
    'Reuters World': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
    'AP News': 'https://apnews.com/apf-topnews',
    'ISW': 'https://www.understandingwar.org/rss.xml',
    'Defense One': 'https://www.defenseone.com/rss/',
    'Foreign Policy': 'https://foreignpolicy.com/feed/',
    'War on the Rocks': 'https://warontherocks.com/feed/',
    'Crisis Group': 'https://www.crisisgroup.org/crisiswatch/rss',
    'Al Jazeera': 'https://www.aljazeera.com/xml/rss/all.xml',
    'Kyiv Independent': 'https://kyivindependent.com/feed/',
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
        'Conflicts & Crises': [],
        'Military & Security': [],
        'Economy & Energy': [],
        'Diplomacy & Politics': [],
        'Technology & Cyber': [],
        'Other': []
    }
    conflict_keywords = ['ukraine', 'russia', 'gaza', 'israel', 'palestine', 'hamas', 'syria', 'yemen', 'sudan', 'taiwan', 'iran', 'conflict zone', 'ceasefire', 'offensive', 'bombardment', 'casualties', 'humanitarian crisis', 'refugee']
    military_keywords = ['military', 'war', 'defense', 'army', 'navy', 'weapon', 'security', 'terror', 'nato']
    economy_keywords = ['economy', 'energy', 'oil', 'gas', 'trade', 'market', 'sanction', 'dollar', 'euro', 'inflation', 'gdp']
    diplomacy_keywords = ['diplomacy', 'treaty', 'summit', 'election', 'government', 'minister', 'president', 'ambassador']
    tech_keywords = ['cyber', 'technology', 'AI', 'chip', 'semiconductor', 'hack', 'digital', 'software']
    for article in articles:
        text = (article['title'] + ' ' + article['summary']).lower()
        if any(keyword in text for keyword in conflict_keywords):
            categories['Conflicts & Crises'].append(article)
        elif any(keyword in text for keyword in military_keywords):
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
    
    html_parts = []
    html_parts.append('<!DOCTYPE html>')
    html_parts.append('<html>')
    html_parts.append('<head>')
    html_parts.append('<meta charset="UTF-8">')
    html_parts.append('<style>')
    html_parts.append('body{font-family:Georgia,serif;max-width:700px;margin:0 auto;padding:20px;background-color:#f5f5f5;color:#333}')
    html_parts.append('.header{background-color:#1a1a1a;color:#fff;padding:30px;text-align:center;border-radius:8px 8px 0 0}')
    html_parts.append('.header h1{margin:0;font-size:28px;font-weight:300;letter-spacing:2px}')
    html_parts.append('.date{color:#999;font-size:14px;margin-top:10px}')
    html_parts.append('.content{background-color:#fff;padding:30px;border-radius:0 0 8px 8px}')
    html_parts.append('.category{margin-bottom:35px}')
    html_parts.append('.category-title{font-size:20px;color:#1a1a1a;border-bottom:2px solid #e0e0e0;padding-bottom:10px;margin-bottom:20px;font-weight:600}')
    html_parts.append('.article{margin-bottom:25px;padding-bottom:20px;border-bottom:1px solid #f0f0f0}')
    html_parts.append('.article:last-child{border-bottom:none}')
    html_parts.append('.article-title{font-size:16px;font-weight:600;color:#2c3e50;margin-bottom:8px;line-height:1.4}')
    html_parts.append('.article-title a{color:#2c3e50;text-decoration:none}')
    html_parts.append('.article-title a:hover{color:#3498db}')
    html_parts.append('.article-meta{font-size:13px;color:#7f8c8d;margin-bottom:8px}')
    html_parts.append('.article-summary{font-size:14px;line-height:1.6;color:#555}')
    html_parts.append('.footer{text-align:center;padding:20px;color:#999;font-size:12px}')
    html_parts.append('</style>')
    html_parts.append('</head>')
    html_parts.append('<body>')
    html_parts.append('<div class="header">')
    html_parts.append('<h1>GEOPOLITICAL INTELLIGENCE BRIEF</h1>')
    html_parts.append('<div class="date">' + current_time.strftime('%A, %B %d, %Y') + '</div>')
    html_parts.append('</div>')
    html_parts.append('<div class="content">')
    
    for category_name, articles in categories.items():
        if articles:
            html_parts.append('<div class="category">')
            html_parts.append('<h2 class="category-title">' + category_name + '</h2>')
            for article in articles[:5]:
                html_parts.append('<div class="article">')
                html_parts.append('<div class="article-title">')
                html_parts.append('<a href="' + article['link'] + '" target="_blank">' + article['title'] + '</a>')
                html_parts.append('</div>')
                html_parts.append('<div class="article-meta">' + article['source'] + '</div>')
                html_parts.append('<div class="article-summary">' + article['summary'] + '</div>')
                html_parts.append('</div>')
            html_parts.append('</div>')
    
    html_parts.append('</div>')
    html_parts.append('<div class="footer">')
    html_parts.append('Geopolitical Intelligence Brief | Automated Daily Report')
    html_parts.append('</div>')
    html_parts.append('</body>')
    html_parts.append('</html>')
    
    return ''.join(html_parts)

def send_email(html_content):
    try:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "from": SENDER_EMAIL,
            "to": [RECIPIENT_EMAIL],
            "subject": f'Geopolitical Brief - {datetime.now(pytz.timezone("Europe/Stockholm")).strftime("%B %d, %Y")}',
            "html": html_content
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"Email sent successfully via Resend!")
            return True
        else:
            print(f"Error sending email: {response.status_code} - {response.text}")
            return False
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
    print("Brief generation complete!")

def run_scheduler():
    schedule.every().day.at("05:00").do(generate_and_send_brief)
    print("Scheduler started. Waiting for 07:00 Stockholm time...")
    while True:
        schedule.run_pending()
        time.sleep(60)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    def log_message(self, format, *args):
        pass

def run_health_check_server():
    health_port = int(os.environ.get('PORT', 10000))
    print(f"Health check server starting on port {health_port}")
    server = HTTPServer(('0.0.0.0', health_port), HealthCheckHandler)
    server.serve_forever()

if __name__ == "__main__":
    health_thread = threading.Thread(target=run_health_check_server, daemon=True)
    health_thread.start()
    print("Running initial brief...")
    generate_and_send_brief()
    run_scheduler()

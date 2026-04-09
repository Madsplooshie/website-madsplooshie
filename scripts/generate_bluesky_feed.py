#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from html import escape

# Your Bluesky handle
BLUESKY_HANDLE = "madsplooshie.neocities.org"

def fetch_bluesky_feed(handle):
    """Fetch RSS feed from Bluesky"""
    rss_url = f"https://bsky.app/profile/{handle}/rss"
    try:
        response = requests.get(rss_url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        return None

def parse_rss(rss_content):
    """Parse RSS feed and extract posts"""
    try:
        root = ET.fromstring(rss_content)
        # Bluesky RSS namespace
        ns = {'content': 'http://purl.org/rss/1.0/modules/content/'}
        
        posts = []
        for item in root.findall('.//item'):
            title = item.findtext('title', '')
            link = item.findtext('link', '')
            pubdate = item.findtext('pubDate', '')
            description = item.findtext('description', '')
            
            posts.append({
                'title': escape(title),
                'link': link,
                'pubdate': pubdate,
                'description': description[:200] + '...' if len(description) > 200 else description
            })
        
        return posts[:10]  # Return last 10 posts
    except ET.ParseError as e:
        print(f"Error parsing RSS: {e}")
        return []

def generate_html(posts):
    """Generate HTML for the feed"""
    html = '''<div class="bluesky-feed-container">
    <div class="bluesky-feed">
        <h2>Latest from Bluesky</h2>
        <div class="feed-posts">
'''
    
    if not posts:
        html += '            <p><em>No posts found. Check back soon!</em></p>\n'
    else:
        for post in posts:
            html += f'''            <div class="feed-post">
                <a href="{post['link']}" target="_blank" rel="noopener noreferrer">
                    <strong>{post['title']}</strong>
                </a>
                <p class="post-date">{post['pubdate']}</p>
                <p class="post-content">{escape(post['description'])}</p>
            </div>
'''
    
    html += '''        </div>
    </div>
</div>'''
    
    return html

def main():
    print("Fetching Bluesky feed...")
    rss_content = fetch_bluesky_feed(BLUESKY_HANDLE)
    
    if not rss_content:
        print("Failed to fetch feed. Exiting.")
        return
    
    print("Parsing feed...")
    posts = parse_rss(rss_content)
    print(f"Found {len(posts)} posts")
    
    print("Generating HTML...")
    html = generate_html(posts)
    
    # Write to file
    output_path = "bluesky-feed.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Feed saved to {output_path}")

if __name__ == "__main__":
    main()

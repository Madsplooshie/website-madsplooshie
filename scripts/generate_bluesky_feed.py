#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from html import escape
import json

# Your Bluesky handle
BLUESKY_HANDLE = "madsplooshie.neocities.org"

def fetch_bluesky_feed(handle):
    """Fetch RSS feed from Bluesky"""
    rss_url = f"https://bsky.app/profile/{handle}/rss"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(rss_url, headers=headers, timeout=15)
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
        items = root.findall('.//item')
        if not items:
            print("No items found in RSS feed")
            return []

        for item in items[:10]:  # Get last 10 posts (increased limit)
            title_elem = item.find('title')
            link_elem = item.find('link')
            pubdate_elem = item.find('pubDate')
            description_elem = item.find('description')

            title = title_elem.text if title_elem is not None else ""
            link = link_elem.text if link_elem is not None else ""
            pubdate = pubdate_elem.text if pubdate_elem is not None else ""
            description = description_elem.text if description_elem is not None else ""

            # Clean up the description
            description = description.replace('<br>', '\n').replace('<br/>', '\n')
            # Remove HTML tags
            import re
            description = re.sub(r'<[^>]+>', '', description)
            # Truncate if too long
            if len(description) > 150:
                description = description[:150] + "..."

            posts.append({
                'title': escape(title.strip()),
                'link': link.strip(),
                'pubdate': pubdate.strip(),
                'description': escape(description.strip())
            })

        # Ensure newest posts appear first
        def parse_date(date_str):
            try:
                return parsedate_to_datetime(date_str)
            except Exception:
                return datetime.min

        posts.sort(key=lambda post: parse_date(post['pubdate']), reverse=True)
        return posts
    except ET.ParseError as e:
        print(f"Error parsing RSS: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error parsing RSS: {e}")
        return []

def generate_html(posts):
    """Generate HTML for the feed"""
    html = '''<div class="bluesky-feed-container">
    <div class="bluesky-feed">
        <h2><svg xmlns="http://www.w3.org/2000/svg" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewBox="0 0 511.999 452.266" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"><path fill="#0085FF" fill-rule="nonzero" d="M110.985 30.442c58.695 44.217 121.837 133.856 145.013 181.961 23.176-48.105 86.322-137.744 145.016-181.961 42.361-31.897 110.985-56.584 110.985 21.96 0 15.681-8.962 131.776-14.223 150.628-18.272 65.516-84.873 82.228-144.112 72.116 103.55 17.68 129.889 76.238 73 134.8-108.04 111.223-155.288-27.905-167.385-63.554-3.489-10.262-2.991-10.498-6.561 0-12.098 35.649-59.342 174.777-167.382 63.554-56.89-58.562-30.551-117.12 72.999-134.8-59.239 10.112-125.84-6.6-144.112-72.116C8.962 184.178 0 68.083 0 52.402c0-78.544 68.633-53.857 110.985-21.96z"/></svg> Posts de Bluesky</h2>
        <div class="feed-posts">
'''

    if not posts:
        html += '''            <div class="feed-post">
                <p><em>No posts found. Check back soon! 🌸</em></p>
            </div>
'''
    else:
        post_count = len(posts)
        for post in posts:
            # Format date
            try:
                # Parse and format date
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(post['pubdate'])
                formatted_date = dt.strftime("%b %d, %Y")
            except:
                formatted_date = "Recent"

            html += f'''            <div class="feed-post">
                <div class="post-header">
                    <span class="post-title">Nueva publicación de Bluesky</span>
                    <span class="post-date">{formatted_date}</span>
                </div>
                <p class="post-content">{post['description']}</p>
                <a href="{post['link']}" target="_blank" rel="noopener noreferrer" class="read-more">
                    Leer en Bluesky →
                </a>
            </div>
'''

        # Add a note if fewer than 5 posts
        if post_count < 5:
            html += f'''            <div class="feed-post feed-note">
                <p><em>📝 Mas posts se mostraran en Bluesky en lo que los voy agregando! Por ahora, se estan mostrando {post_count} de mis ultimos posts.</em></p>
            </div>
'''

    html += '''        </div>
        <div class="feed-footer">
            <a href="https://bsky.app/profile/madsplooshie.neocities.org" target="_blank" class="follow-link">
                Siganme en Bluesky! <svg xmlns="http://www.w3.org/2000/svg" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewBox="0 0 511.999 452.266" style="width: 16px; height: 16px; vertical-align: middle; margin-left: 4px;"><path fill="#0085FF" fill-rule="nonzero" d="M110.985 30.442c58.695 44.217 121.837 133.856 145.013 181.961 23.176-48.105 86.322-137.744 145.016-181.961 42.361-31.897 110.985-56.584 110.985 21.96 0 15.681-8.962 131.776-14.223 150.628-18.272 65.516-84.873 82.228-144.112 72.116 103.55 17.68 129.889 76.238 73 134.8-108.04 111.223-155.288-27.905-167.385-63.554-3.489-10.262-2.991-10.498-6.561 0-12.098 35.649-59.342 174.777-167.382 63.554-56.89-58.562-30.551-117.12 72.999-134.8-59.239 10.112-125.84-6.6-144.112-72.116C8.962 184.178 0 68.083 0 52.402c0-78.544 68.633-53.857 110.985-21.96z"/></svg>
            </a>
        </div>
    </div>
</div>'''

    return html

def main():
    print("🌸 Fetching Bluesky feed...")
    rss_content = fetch_bluesky_feed(BLUESKY_HANDLE)

    if not rss_content:
        print("❌ Failed to fetch feed. Exiting.")
        # Generate fallback HTML
        html = '''<div class="bluesky-feed-container">
    <div class="bluesky-feed">
        <h2><svg xmlns="http://www.w3.org/2000/svg" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewBox="0 0 511.999 452.266" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"><path fill="#0085FF" fill-rule="nonzero" d="M110.985 30.442c58.695 44.217 121.837 133.856 145.013 181.961 23.176-48.105 86.322-137.744 145.016-181.961 42.361-31.897 110.985-56.584 110.985 21.96 0 15.681-8.962 131.776-14.223 150.628-18.272 65.516-84.873 82.228-144.112 72.116 103.55 17.68 129.889 76.238 73 134.8-108.04 111.223-155.288-27.905-167.385-63.554-3.489-10.262-2.991-10.498-6.561 0-12.098 35.649-59.342 174.777-167.382 63.554-56.89-58.562-30.551-117.12 72.999-134.8-59.239 10.112-125.84-6.6-144.112-72.116C8.962 184.178 0 68.083 0 52.402c0-78.544 68.633-53.857 110.985-21.96z"/></svg> Latest from Bluesky</h2>
        <div class="feed-posts">
            <div class="feed-post">
                <p><em>Unable to load feed right now. 🌸</em></p>
                <a href="https://bsky.app/profile/madsplooshie.neocities.org" target="_blank" class="follow-link">
                    Visit my Bluesky profile →
                </a>
            </div>
        </div>
    </div>
</div>'''
    else:
        print("📄 Parsing feed...")
        posts = parse_rss(rss_content)
        print(f"✨ Found {len(posts)} posts")

        print("🎨 Generating HTML...")
        html = generate_html(posts)

    # Write to file
    output_path = "bluesky-feed.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"💾 Feed saved to {output_path}")

if __name__ == "__main__":
    main()

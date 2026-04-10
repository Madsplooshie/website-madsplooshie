#!/usr/bin/env python3
import requests
from datetime import datetime
from html import escape

# Your Bluesky handle
BLUESKY_HANDLE = "madsplooshie.neocities.org"
MAX_POSTS = 5

def fetch_bluesky_feed(handle):
    """Fetch posts from Bluesky public API (includes image embeds)"""
    api_url = f"https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor={handle}&limit={MAX_POSTS}&filter=posts_no_replies"
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching Bluesky API: {e}")
        return None

def parse_api_response(data):
    """Parse Bluesky API response and extract posts with images"""
    posts = []
    feed = data.get('feed', [])
    if not feed:
        print("No posts found in API response")
        return []

    for item in feed[:MAX_POSTS]:
        post = item.get('post', {})
        record = post.get('record', {})

        text = record.get('text', '')
        created_at = record.get('createdAt', '')
        uri = post.get('uri', '')

        # Build the bsky.app link from the AT URI
        # Format: at://did:plc:xxx/app.bsky.feed.post/yyy
        link = ''
        if uri:
            parts = uri.replace('at://', '').split('/')
            if len(parts) >= 3:
                did = parts[0]
                rkey = parts[2]
                link = f"https://bsky.app/profile/{BLUESKY_HANDLE}/post/{rkey}"

        # Get thumbnail from image embed if present
        thumbnail = ''
        embed = post.get('embed', {})
        embed_type = embed.get('$type', '')
        if embed_type == 'app.bsky.embed.images#view':
            images = embed.get('images', [])
            if images:
                thumbnail = images[0].get('thumb', '')
        elif embed_type == 'app.bsky.embed.recordWithMedia#view':
            media = embed.get('media', {})
            if media.get('$type') == 'app.bsky.embed.images#view':
                images = media.get('images', [])
                if images:
                    thumbnail = images[0].get('thumb', '')

        # Truncate text if too long
        description = text
        if len(description) > 200:
            description = description[:200] + "..."

        # Parse date
        formatted_date = "Recent"
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                formatted_date = dt.strftime("%b %d, %Y")
            except Exception:
                pass

        posts.append({
            'description': escape(description),
            'link': link,
            'date': formatted_date,
            'thumbnail': thumbnail,
        })

    return posts

def generate_html(posts):
    """Generate HTML for the feed with speech bubbles and optional thumbnails"""
    html = '''<div class="bluesky-feed-container">
    <div class="bluesky-feed">
        <h2><svg xmlns="http://www.w3.org/2000/svg" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewBox="0 0 511.999 452.266" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"><path fill="#0085FF" fill-rule="nonzero" d="M110.985 30.442c58.695 44.217 121.837 133.856 145.013 181.961 23.176-48.105 86.322-137.744 145.016-181.961 42.361-31.897 110.985-56.584 110.985 21.96 0 15.681-8.962 131.776-14.223 150.628-18.272 65.516-84.873 82.228-144.112 72.116 103.55 17.68 129.889 76.238 73 134.8-108.04 111.223-155.288-27.905-167.385-63.554-3.489-10.262-2.991-10.498-6.561 0-12.098 35.649-59.342 174.777-167.382 63.554-56.89-58.562-30.551-117.12 72.999-134.8-59.239 10.112-125.84-6.6-144.112-72.116C8.962 184.178 0 68.083 0 52.402c0-78.544 68.633-53.857 110.985-21.96z"/></svg> Posts de Bluesky</h2>
        <div class="feed-posts">
'''

    if not posts:
        html += '''            <div class="feed-post-row">
                <img src="Media/pfp.png" alt="Madsplooshie" class="feed-avatar">
                <div class="feed-post">
                    <p><em>No posts found. Check back soon! 🌸</em></p>
                </div>
            </div>
'''
    else:
        post_count = len(posts)
        for post in posts:
            # Build thumbnail HTML if image exists
            thumb_html = ''
            if post['thumbnail']:
                thumb_html = f'\n                    <a href="{post["link"]}" target="_blank" rel="noopener noreferrer"><img src="{post["thumbnail"]}" alt="Post image" class="post-thumbnail"></a>'

            html += f'''            <div class="feed-post-row">
                <img src="Media/pfp.png" alt="Madsplooshie" class="feed-avatar">
                <div class="feed-post">
                    <div class="post-header">
                        <span class="post-title">Nueva publicación de Bluesky</span>
                        <span class="post-date">{post['date']}</span>
                    </div>
                    <div class="post-body">{thumb_html}
                        <p class="post-content">{post['description']}</p>
                    </div>
                    <a href="{post['link']}" target="_blank" rel="noopener noreferrer" class="read-more">
                        Leer en Bluesky →
                    </a>
                </div>
            </div>
'''

        # Add a note if fewer than max posts
        if post_count < MAX_POSTS:
            html += f'''            <div class="feed-post-row">
                <img src="Media/pfp.png" alt="Madsplooshie" class="feed-avatar">
                <div class="feed-post feed-note">
                    <p><em>📝 Mas posts se mostraran en Bluesky en lo que los voy agregando! Por ahora, se estan mostrando {post_count} de mis ultimos posts.</em></p>
                </div>
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
    data = fetch_bluesky_feed(BLUESKY_HANDLE)

    if not data:
        print("❌ Failed to fetch feed. Exiting.")
        html = '''<div class="bluesky-feed-container">
    <div class="bluesky-feed">
        <h2><svg xmlns="http://www.w3.org/2000/svg" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewBox="0 0 511.999 452.266" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;"><path fill="#0085FF" fill-rule="nonzero" d="M110.985 30.442c58.695 44.217 121.837 133.856 145.013 181.961 23.176-48.105 86.322-137.744 145.016-181.961 42.361-31.897 110.985-56.584 110.985 21.96 0 15.681-8.962 131.776-14.223 150.628-18.272 65.516-84.873 82.228-144.112 72.116 103.55 17.68 129.889 76.238 73 134.8-108.04 111.223-155.288-27.905-167.385-63.554-3.489-10.262-2.991-10.498-6.561 0-12.098 35.649-59.342 174.777-167.382 63.554-56.89-58.562-30.551-117.12 72.999-134.8-59.239 10.112-125.84-6.6-144.112-72.116C8.962 184.178 0 68.083 0 52.402c0-78.544 68.633-53.857 110.985-21.96z"/></svg> Posts de Bluesky</h2>
        <div class="feed-posts">
            <div class="feed-post-row">
                <img src="Media/pfp.png" alt="Madsplooshie" class="feed-avatar">
                <div class="feed-post">
                    <p><em>Unable to load feed right now. 🌸</em></p>
                    <a href="https://bsky.app/profile/madsplooshie.neocities.org" target="_blank" class="follow-link">
                        Visit my Bluesky profile →
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>'''
    else:
        print("📄 Parsing feed...")
        posts = parse_api_response(data)
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

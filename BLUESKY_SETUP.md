# Bluesky Feed Setup Guide

This guide walks you through setting up automatic Bluesky feed generation using GitHub Actions.

## What This Does
- Automatically fetches your latest Bluesky posts every 2 hours
- Converts the RSS feed to HTML
- Commits the generated HTML back to your repo
- You can then pull this HTML into your Neocities site

## Setup Steps

### 1. Initialize a Git Repository & Push to GitHub

If you haven't already:

```bash
cd C:\Users\Andre\Documents\StreamStuff\WebSiteStuff
git init
git add .
git commit -m "Initial commit"
```

Then create a new repository on GitHub at github.com/new, and push:

```bash
git remote add origin https://github.com/YOUR_USERNAME/websitestuff.git
git branch -M main
git push -u origin main
```

### 2. Configure Bluesky Handle

Edit `scripts/generate_bluesky_feed.py` and update this line with your actual Bluesky handle:

```python
BLUESKY_HANDLE = "madsplooshie.neocities.org"  # Change this to your handle
```

You can find your handle by visiting your Bluesky profile - it's the part after @

### 3. Test the Script Locally

```bash
pip install requests
python scripts/generate_bluesky_feed.py
```

This will create `bluesky-feed.html` in your repo root with your latest posts.

### 4. Integrate Into Your HTML

The script generates an HTML file that you can embed anywhere in your site. Add to your `index.html`:

**In the `<head>` section:**
```html
<link rel="stylesheet" href="bluesky-feed.css">
```

**Where you want the feed to display (e.g., in the center content area):**
```html
<div class="contentbar">
    <div class="iframe-section">
        <div class="content" id="bluesky-feed-wrapper">
            <p>Loading feed...</p>
        </div>
    </div>
</div>

<script>
    // Load the generated feed
    fetch('bluesky-feed.html')
        .then(response => response.text())
        .then(html => {
            document.getElementById('bluesky-feed-wrapper').innerHTML = html;
        })
        .catch(error => console.error('Error loading feed:', error));
</script>
```

### 5. GitHub Actions Will Run Automatically

Once you push to GitHub, the workflow will:
- Run on the schedule you set (default: every 2 hours)
- Fetch your Bluesky feed
- Generate new HTML
- Automatically commit changes back to the repo

You can manually trigger it from the GitHub Actions tab anytime.

### 6. Pull Updated Feed to Neocities

After the GitHub Action runs, pull the latest from GitHub:

```bash
git pull origin main
```

The `bluesky-feed.html` file will be updated. You can then upload it to Neocities manually, or set up Neocities to auto-sync from your GitHub repo.

## Customization

### Change Update Frequency

Edit `.github/workflows/bluesky-feed.yml` and modify the cron schedule:

```yaml
- cron: '0 */1 * * *'   # Every hour
- cron: '0 9,17 * * *'  # 9 AM and 5 PM daily
- cron: '0 0 * * 0'     # Weekly (Sunday at midnight)
```

### Adjust Number of Posts

In `scripts/generate_bluesky_feed.py`, change this line:

```python
return posts[:10]  # Change 10 to however many you want
```

### Customize Styling

Edit `bluesky-feed.css` to match your site's colors and aesthetic. The file uses your existing CSS variables like `--text-accent` and `--link-color`.

## Troubleshooting

- **Feed not updating**: Check the "Actions" tab in your GitHub repo for error logs
- **AttributeError with namespace**: Bluesky's RSS format may have changed - check the script
- **Not syncing to Neocities**: You'll need to manually pull from GitHub and reupload, OR set up a Neocities API integration

## Alternative: Direct Fetch (Simpler)

If you prefer not to use GitHub Actions, you can just fetch and display the feed directly in JavaScript embedded in your HTML (though this may be slower):

```javascript
fetch('https://bsky.app/profile/madsplooshie.neocities.org/rss')
    .then(r => r.text())
    .then(rss => {
        // Parse and display XML...
    });
```

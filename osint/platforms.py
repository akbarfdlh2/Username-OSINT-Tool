"""
Daftar platform yang dicek.
Tambah platform baru dengan pola yang sama.

Format:
  "Platform Name": {
      "url": "https://platform.com/{}",   # {} diganti username
      "category": "Social",
      "check": "status_code" | "content", # cara verifikasi
      "content_present": "text",          # kalau check == "content": teks ini harus ADA
      "content_absent": "text",           # kalau check == "content": teks ini harus TIDAK ADA
      "not_found_code": 404,              # override default 404
  }
"""

PLATFORMS: dict[str, dict] = {
    # ─── Developer ───────────────────────────────────────────────────────────
    "GitHub": {
        "url": "https://github.com/{}",
        "category": "Developer",
        "check": "status_code",
    },
    "GitLab": {
        "url": "https://gitlab.com/{}",
        "category": "Developer",
        "check": "status_code",
    },
    "Bitbucket": {
        "url": "https://bitbucket.org/{}",
        "category": "Developer",
        "check": "status_code",
    },
    "npm": {
        "url": "https://www.npmjs.com/~{}",
        "category": "Developer",
        "check": "status_code",
    },
    "PyPI": {
        "url": "https://pypi.org/user/{}",
        "category": "Developer",
        "check": "status_code",
    },
    "Replit": {
        "url": "https://replit.com/@{}",
        "category": "Developer",
        "check": "status_code",
    },
    "Codepen": {
        "url": "https://codepen.io/{}",
        "category": "Developer",
        "check": "status_code",
    },
    "Hackernews": {
        "url": "https://news.ycombinator.com/user?id={}",
        "category": "Developer",
        "check": "content",
        "content_present": "user?id=",
        "content_absent": "No such user",
    },
    "DEV.to": {
        "url": "https://dev.to/{}",
        "category": "Developer",
        "check": "status_code",
    },
    "Hashnode": {
        "url": "https://hashnode.com/@{}",
        "category": "Developer",
        "check": "status_code",
    },

    # ─── Social Media ─────────────────────────────────────────────────────────
    "Twitter/X": {
        "url": "https://twitter.com/{}",
        "category": "Social",
        "check": "content",
        "content_absent": "This account doesn\u2019t exist",
    },
    "Instagram": {
        "url": "https://www.instagram.com/{}",
        "category": "Social",
        "check": "content",
        "content_absent": "Sorry, this page isn\u2019t available",
    },
    "TikTok": {
        "url": "https://www.tiktok.com/@{}",
        "category": "Social",
        "check": "status_code",
    },
    "Facebook": {
        "url": "https://www.facebook.com/{}",
        "category": "Social",
        "check": "status_code",
    },
    "Pinterest": {
        "url": "https://www.pinterest.com/{}",
        "category": "Social",
        "check": "status_code",
    },
    "Snapchat": {
        "url": "https://www.snapchat.com/add/{}",
        "category": "Social",
        "check": "status_code",
    },
    "Tumblr": {
        "url": "https://{}.tumblr.com",
        "category": "Social",
        "check": "status_code",
    },

    # ─── Professional ─────────────────────────────────────────────────────────
    "LinkedIn": {
        "url": "https://www.linkedin.com/in/{}",
        "category": "Professional",
        "check": "status_code",
    },
    "AngelList": {
        "url": "https://angel.co/u/{}",
        "category": "Professional",
        "check": "status_code",
    },
    "Keybase": {
        "url": "https://keybase.io/{}",
        "category": "Professional",
        "check": "status_code",
    },

    # ─── Gaming ───────────────────────────────────────────────────────────────
    "Steam": {
        "url": "https://steamcommunity.com/id/{}",
        "category": "Gaming",
        "check": "content",
        "content_absent": "The specified profile could not be found",
    },
    "Twitch": {
        "url": "https://www.twitch.tv/{}",
        "category": "Gaming",
        "check": "status_code",
    },
    "Roblox": {
        "url": "https://www.roblox.com/user.aspx?username={}",
        "category": "Gaming",
        "check": "content",
        "content_absent": "Page cannot be found",
    },
    "Chess.com": {
        "url": "https://www.chess.com/member/{}",
        "category": "Gaming",
        "check": "status_code",
    },

    # ─── Creative ─────────────────────────────────────────────────────────────
    "Behance": {
        "url": "https://www.behance.net/{}",
        "category": "Creative",
        "check": "status_code",
    },
    "Dribbble": {
        "url": "https://dribbble.com/{}",
        "category": "Creative",
        "check": "status_code",
    },
    "DeviantArt": {
        "url": "https://www.deviantart.com/{}",
        "category": "Creative",
        "check": "status_code",
    },
    "SoundCloud": {
        "url": "https://soundcloud.com/{}",
        "category": "Creative",
        "check": "status_code",
    },
    "Spotify": {
        "url": "https://open.spotify.com/user/{}",
        "category": "Creative",
        "check": "status_code",
    },
    "Last.fm": {
        "url": "https://www.last.fm/user/{}",
        "category": "Creative",
        "check": "status_code",
    },
    "Flickr": {
        "url": "https://www.flickr.com/people/{}",
        "category": "Creative",
        "check": "status_code",
    },
    "500px": {
        "url": "https://500px.com/p/{}",
        "category": "Creative",
        "check": "status_code",
    },

    # ─── Forum / Community ────────────────────────────────────────────────────
    "Reddit": {
        "url": "https://www.reddit.com/user/{}",
        "category": "Forum",
        "check": "content",
        "content_absent": "Sorry, nobody on Reddit goes by that name",
    },
    "Quora": {
        "url": "https://www.quora.com/profile/{}",
        "category": "Forum",
        "check": "status_code",
    },
    "Medium": {
        "url": "https://medium.com/@{}",
        "category": "Forum",
        "check": "status_code",
    },
    "Substack": {
        "url": "https://substack.com/@{}",
        "category": "Forum",
        "check": "status_code",
    },
    "Disqus": {
        "url": "https://disqus.com/by/{}/",
        "category": "Forum",
        "check": "status_code",
    },

    # ─── Tech / Productivity ──────────────────────────────────────────────────
    "Product Hunt": {
        "url": "https://www.producthunt.com/@{}",
        "category": "Tech",
        "check": "status_code",
    },
    "Kaggle": {
        "url": "https://www.kaggle.com/{}",
        "category": "Tech",
        "check": "status_code",
    },
    "HuggingFace": {
        "url": "https://huggingface.co/{}",
        "category": "Tech",
        "check": "status_code",
    },
    "Stack Overflow": {
        "url": "https://stackoverflow.com/users/{}",
        "category": "Tech",
        "check": "status_code",
    },
    "Docker Hub": {
        "url": "https://hub.docker.com/u/{}",
        "category": "Tech",
        "check": "status_code",
    },

    # ─── Indonesia / SEA ──────────────────────────────────────────────────────
    "Kaskus": {
        "url": "https://www.kaskus.co.id/profile/{}",
        "category": "Indonesia",
        "check": "status_code",
    },
    "Tokopedia": {
        "url": "https://www.tokopedia.com/{}",
        "category": "Indonesia",
        "check": "status_code",
    },
    "Shopee": {
        "url": "https://shopee.co.id/{}",
        "category": "Indonesia",
        "check": "status_code",
    },
}

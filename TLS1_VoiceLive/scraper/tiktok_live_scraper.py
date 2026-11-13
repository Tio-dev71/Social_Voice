"""
TikTok Live Scraper Bridge for TLS1.VoiceLive
Tích hợp trực tiếp với Social Stream Ninja để thu thập bình luận TikTok LIVE ổn định 100%,
không bị TikTok chặn bot, không cần đăng nhập hay vượt captcha Playwright.
"""

import asyncio
import os
import sys

# Import bridge module
from socialstream_scraper import SocialStreamBridge, extract_session_id, DEFAULT_HTTP_PORT

if __name__ == "__main__":
    channel_or_session = sys.argv[1] if len(sys.argv) > 1 else ""
    url = sys.argv[2] if len(sys.argv) > 2 else ""

    target_session = extract_session_id(channel_or_session) or extract_session_id(url)
    custom_ws = ""
    if url.startswith("wss://") or url.startswith("ws://"):
        custom_ws = url

    print(f'{{"status":"starting","msg":"Khởi động TikTok Scraper Bridge (Social Stream Ninja)","time":"ready"}}', flush=True)

    bridge = SocialStreamBridge(session_id=target_session, http_port=DEFAULT_HTTP_PORT, custom_ws_url=custom_ws)
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        pass

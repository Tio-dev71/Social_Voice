"""
Live Chat Scraper for TLS1.VoiceLive
Hỗ trợ:
1. Social Stream Ninja (YouTube & TikTok qua WebSocket hoặc HTTP Webhook)
2. YouTube Live Chat / Twitch / Generic
"""

import asyncio
import json
import os
import sys
from datetime import datetime

from socialstream_scraper import SocialStreamBridge, extract_session_id, DEFAULT_HTTP_PORT

PLATFORM_SELECTORS = {
    "youtube": {
        "url_template": "https://www.youtube.com/live_chat?is_popout=1&v={channel}",
        "container": "yt-live-chat-text-message-renderer",
        "author": "#author-name",
        "message": "#message",
    },
    "tiktok": {
        "url_template": "https://www.tiktok.com/@{channel}/live",
        "container": "div[data-e2e='chat-message']",
        "author": "span[data-e2e='chat-username']",
        "message": "span[data-e2e='chat-message-text']",
    },
    "generic": {
        "url_template": "{url}",
        "container": None, "author": None, "message": None,
    },
}

def now():
    return datetime.now().strftime("%H:%M:%S")

async def scrape(platform_id: str, url: str, channel: str):
    # Kiểm tra nếu là Social Stream Ninja
    is_social_stream = (
        platform_id.lower() in ("socialstream", "social_stream", "ssn", "ninja")
        or "socialstream" in url.lower()
        or "ninja" in url.lower()
        or "session=" in url.lower()
        or "127.0.0.1:9999" in url
    )

    if is_social_stream:
        session = extract_session_id(channel) or extract_session_id(url)
        custom_ws = url if (url.startswith("ws://") or url.startswith("wss://")) else ""
        bridge = SocialStreamBridge(session_id=session, http_port=DEFAULT_HTTP_PORT, custom_ws_url=custom_ws)
        await bridge.run()
        return

    # Nếu là YouTube hoặc nền tảng khác, thử Playwright nếu có, nếu không có thì fallback sang Social Stream Bridge
    try:
        from playwright.async_api import async_playwright
        from bs4 import BeautifulSoup
    except ImportError:
        # Nếu không có Playwright: fallback sang Social Stream Bridge
        print(json.dumps({
            "status": "ready",
            "msg": f"Khởi động bridge nhận {platform_id} từ Social Stream Ninja (HTTP 9999)...",
            "time": now()
        }, ensure_ascii=False), flush=True)
        session = extract_session_id(channel) or extract_session_id(url)
        bridge = SocialStreamBridge(session_id=session, http_port=DEFAULT_HTTP_PORT)
        await bridge.run()
        return

    config = PLATFORM_SELECTORS.get(platform_id, PLATFORM_SELECTORS["generic"])
    if platform_id in ("youtube", "tiktok"):
        final_url = config["url_template"].format(channel=channel, url=url)
    else:
        final_url = url

    print(json.dumps({"status": "connecting", "url": final_url, "time": now()}, ensure_ascii=False), flush=True)

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True, args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox", "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process"
            ])
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            await page.add_init_script("""Object.defineProperty(navigator,'webdriver',{get:()=>undefined});window.chrome={runtime:{}};""")

            await page.goto(final_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(5000)
            print(json.dumps({"status": "connected", "time": now()}, ensure_ascii=False), flush=True)
        except Exception as e:
            print(json.dumps({"status": "error", "msg": str(e), "time": now()}, ensure_ascii=False), flush=True)
            # Thử fallback sang SocialStreamBridge
            bridge = SocialStreamBridge(session_id="", http_port=DEFAULT_HTTP_PORT)
            await bridge.run()
            return

        # Skip initial comments
        seen = set()
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        cs = config.get("container")
        a_s = config.get("author")
        m_s = config.get("message")
        for el in (soup.select(cs) if cs else soup.find_all(["div", "span", "li"], limit=200)):
            try:
                if a_s and m_s:
                    a = el.select_one(a_s)
                    m = el.select_one(m_s)
                    if a and m:
                        seen.add(f"{a.get_text(strip=True)}:{m.get_text(strip=True)}")
                else:
                    t = el.get_text(strip=True)
                    if 3 < len(t) < 500:
                        seen.add(f"User:{t}")
            except Exception:
                continue

        print(json.dumps({"status": "ready", "skipped": len(seen), "msg": f"Bỏ qua {len(seen)} bình luận cũ", "time": now()}, ensure_ascii=False), flush=True)

        total = 0
        heartbeat = 0

        while True:
            try:
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                elements = soup.select(cs) if cs else soup.find_all(["div", "span", "li"], limit=200)

                found = 0
                for el in elements:
                    try:
                        author = "User"
                        message = ""
                        if a_s and m_s:
                            a_el = el.select_one(a_s)
                            m_el = el.select_one(m_s)
                            if not a_el or not m_el:
                                continue
                            author = a_el.get_text(strip=True)
                            message = m_el.get_text(strip=True)
                        else:
                            text = el.get_text(strip=True)
                            if len(text) < 3 or len(text) > 500:
                                continue
                            message = text
                        if not author or not message:
                            continue

                        key = f"{author}:{message}"
                        if key in seen:
                            continue
                        seen.add(key)

                        print(json.dumps({"type": "comment", "platform": platform_id, "author": author, "message": message, "time": now()}, ensure_ascii=False), flush=True)
                        found += 1
                    except Exception:
                        continue

                if found > 0:
                    total += found
                    heartbeat = 0

                heartbeat += 1
                if heartbeat >= 30:
                    print(json.dumps({"status": "alive", "total": total, "time": now()}, ensure_ascii=False), flush=True)
                    heartbeat = 0

                await page.wait_for_timeout(2000)

            except Exception as e:
                print(json.dumps({"status": "error", "msg": str(e), "time": now()}, ensure_ascii=False), flush=True)
                await page.wait_for_timeout(5000)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"status": "error", "msg": "Usage: python live_chat_scraper.py <platform> <url_or_channel> [channel]"}))
        sys.exit(1)
    platform = sys.argv[1]
    url = sys.argv[2]
    channel = sys.argv[3] if len(sys.argv) > 3 else ""
    try:
        asyncio.run(scrape(platform, url, channel))
    except KeyboardInterrupt:
        pass

"""
Social Stream Ninja Scraper Bridge for TLS1.VoiceLive
Kết nối trực tiếp Social Stream Ninja (YouTube & TikTok) với TLS1.VoiceLive.
Hỗ trợ cả WebSocket Relay (wss://io.socialstream.ninja) và Local HTTP Webhook (http://127.0.0.1:9999/comment).
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime
from aiohttp import web
import websockets

DEFAULT_HTTP_PORT = 9999
WSS_BASE_URL = "wss://io.socialstream.ninja"

def now():
    return datetime.now().strftime("%H:%M:%S")

def extract_session_id(input_str: str) -> str:
    """Trích xuất Session ID từ URL hoặc chuỗi thô."""
    if not input_str:
        return ""
    input_str = input_str.strip()
    
    # URL có query param session=...
    match = re.search(r"[?&]session=([a-zA-Z0-9_-]+)", input_str)
    if match:
        return match.group(1)
    
    # URL dạng /join/SESSION/...
    match = re.search(r"/join/([a-zA-Z0-9_-]+)", input_str)
    if match:
        return match.group(1)
        
    # URL dạng https://io.socialstream.ninja/SESSION/...
    match = re.search(r"socialstream\.ninja(?:/api)?/([a-zA-Z0-9_-]+)", input_str)
    if match:
        return match.group(1)
        
    # Nếu là chuỗi ID thông thường (không phải URL)
    if not input_str.startswith("http://") and not input_str.startswith("https://") and not input_str.startswith("ws://") and not input_str.startswith("wss://"):
        return input_str
        
    return ""

class SocialStreamBridge:
    def __init__(self, session_id: str = "", http_port: int = DEFAULT_HTTP_PORT, custom_ws_url: str = "", static_dir: str = "", enable_speak: bool = False):
        self.session_id = session_id
        self.http_port = http_port
        self.custom_ws_url = custom_ws_url
        self.static_dir = static_dir
        self.enable_speak = enable_speak
        self.seen_messages = set()
        self.seen_queue = []
        self.total_comments = 0
        self.http_runner = None
        self.site = None

    def emit_comment(self, author: str, message: str, platform: str):
        if not message or not author:
            return
            
        author = author.strip()
        message = message.strip()
        
        # Deduplication key
        key = f"{platform}:{author}:{message}"
        if key in self.seen_messages:
            return
            
        self.seen_messages.add(key)
        self.seen_queue.append(key)
        if len(self.seen_queue) > 500:
            oldest = self.seen_queue.pop(0)
            self.seen_messages.discard(oldest)

        self.total_comments += 1
        
        # Chuẩn hóa tên platform cho TLS1
        norm_platform = platform.lower()
        if "tiktok" in norm_platform:
            norm_platform = "tiktok"
        elif "youtube" in norm_platform:
            norm_platform = "youtube"

        output = {
            "type": "comment",
            "platform": norm_platform,
            "author": author,
            "message": message,
            "time": now()
        }
        print(json.dumps(output, ensure_ascii=False), flush=True)

        if self.enable_speak:
            asyncio.create_task(self.speak_text(f"{author} nói: {message}"))

    async def speak_text(self, text: str):
        """Đọc giọng nói trên hệ điều hành (macOS say hoặc Windows TTS)."""
        try:
            clean_text = re.sub(r'[\r\n\t"\']', ' ', text).strip()
            if sys.platform == "darwin":
                # macOS native Vietnamese voice
                proc = await asyncio.create_subprocess_exec("say", "-v", "Linh", clean_text)
                await proc.wait()
            elif sys.platform == "win32":
                ps_cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{clean_text}')"
                proc = await asyncio.create_subprocess_exec("powershell", "-NoProfile", "-Command", ps_cmd)
                await proc.wait()
        except Exception as e:
            pass

    def emit_status(self, status: str, msg: str = ""):
        output = {
            "status": status,
            "msg": msg,
            "time": now()
        }
        print(json.dumps(output, ensure_ascii=False), flush=True)

    # ── HTTP WEBHOOK SERVER ──
    async def start_http_server(self):
        app = web.Application()
        
        async def handle_options(request):
            headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
            return web.Response(status=200, headers=headers)

        async def handle_comment(request):
            headers = {"Access-Control-Allow-Origin": "*"}
            try:
                data = await request.json()
            except Exception:
                try:
                    text = await request.text()
                    data = json.loads(text)
                except Exception as e:
                    return web.json_response({"error": "invalid json", "msg": str(e)}, status=400, headers=headers)

            # Lấy author, message, platform
            author = data.get("author") or data.get("chatname") or data.get("username") or "User"
            message = data.get("message") or data.get("chatmessage") or data.get("content") or ""
            platform = data.get("platform") or data.get("type") or "socialstream"

            if message:
                self.emit_comment(author, message, platform)
                return web.json_response({"status": "received", "total": self.total_comments}, headers=headers)
            
            return web.json_response({"status": "empty_message"}, headers=headers)

        async def handle_status(request):
            headers = {"Access-Control-Allow-Origin": "*"}
            return web.json_response({
                "status": "running",
                "service": "TLS1 SocialStream Scraper Bridge",
                "session_id": self.session_id,
                "total_comments": self.total_comments,
                "time": now()
            }, headers=headers)

        app.router.add_options("/comment", handle_options)
        app.router.add_post("/comment", handle_comment)
        app.router.add_get("/status", handle_status)

        if self.static_dir and os.path.isdir(self.static_dir):
            async def handle_root(request):
                app_path = os.path.join(self.static_dir, "app.html")
                if os.path.exists(app_path):
                    return web.FileResponse(app_path)
                dock_path = os.path.join(self.static_dir, "dock.html")
                if os.path.exists(dock_path):
                    return web.FileResponse(dock_path)
                return await handle_status(request)
            app.router.add_get("/", handle_root)

            # Phục vụ toàn bộ file tĩnh (html, js, css, png, svg...)
            app.router.add_static("/", path=self.static_dir, show_index=True)
            self.emit_status("static_server", f"Đang phục vụ giao diện web tại http://127.0.0.1:{self.http_port}/ (Thư mục: {self.static_dir})")
        else:
            app.router.add_get("/", handle_status)

        runner = web.AppRunner(app)
        await runner.setup()
        self.http_runner = runner
        
        try:
            self.site = web.TCPSite(runner, "127.0.0.1", self.http_port)
            await self.site.start()
            self.emit_status("ready", f"HTTP Webhook đang lắng nghe tại http://127.0.0.1:{self.http_port}/comment")
        except Exception as e:
            self.emit_status("warning", f"Không thể bind cổng HTTP {self.http_port}: {e}")

    # ── WEBSOCKET RELAY CLIENT ──
    async def listen_websocket(self):
        if not self.session_id and not self.custom_ws_url:
            self.emit_status("ready", "Chờ nhận comment qua HTTP Webhook (chưa cấu hình WebSocket Session ID)")
            return

        if self.custom_ws_url:
            uri = self.custom_ws_url
        else:
            # Channel 4 là kênh broadcast chat của extension (in=4, out=3)
            uri = f"{WSS_BASE_URL}/join/{self.session_id}/4/3"

        self.emit_status("connecting", f"Đang kết nối WebSocket Social Stream Ninja: {uri}")

        backoff = 2
        while True:
            try:
                async with websockets.connect(uri, ping_interval=20, ping_timeout=20) as ws:
                    self.emit_status("connected", f"Đã kết nối Social Stream Ninja (Session: {self.session_id})")
                    backoff = 2

                    while True:
                        msg = await ws.recv()
                        try:
                            data = json.loads(msg)
                            if isinstance(data, list):
                                for item in data:
                                    self.process_ws_data(item)
                            elif isinstance(data, dict):
                                self.process_ws_data(data)
                        except json.JSONDecodeError:
                            pass
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.emit_status("reconnecting", f"Mất kết nối WebSocket ({e}), thử lại sau {backoff}s...")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)

    def process_ws_data(self, data: dict):
        # Bỏ qua các message nội bộ không phải chat
        if not data or not isinstance(data, dict):
            return
            
        action = data.get("action")
        if action in ("join", "leave", "keepalive", "ping", "pong", "ssnBridgeChunk"):
            return

        author = data.get("chatname") or data.get("author") or data.get("username")
        message = data.get("chatmessage") or data.get("message") or data.get("content")
        platform = data.get("type") or data.get("platform") or "socialstream"

        if author and message:
            self.emit_comment(author, message, platform)

    async def heartbeat_loop(self):
        while True:
            await asyncio.sleep(30)
            self.emit_status("alive", f"Tổng bình luận đã nhận: {self.total_comments}")

    async def run(self):
        self.emit_status("starting", "Khởi động Social Stream Ninja Bridge cho TLS1.VoiceLive...")
        tasks = [
            asyncio.create_task(self.start_http_server()),
            asyncio.create_task(self.listen_websocket()),
            asyncio.create_task(self.heartbeat_loop())
        ]
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass
        finally:
            if self.http_runner:
                await self.http_runner.cleanup()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Social Stream Ninja Bridge cho TLS1.VoiceLive")
    parser.add_argument("session_pos", nargs="?", default="", help="Session ID hoặc WebSocket URL (vị trí 1)")
    parser.add_argument("port_pos", nargs="?", default=None, help="HTTP Port (vị trí 2)")
    parser.add_argument("--session", default="", help="Social Stream Ninja Session ID")
    parser.add_argument("--port", type=int, default=DEFAULT_HTTP_PORT, help="Port cho HTTP Webhook (mặc định: 9999)")
    parser.add_argument("--static-dir", default="", help="Thư mục chứa giao diện Social Stream")
    parser.add_argument("--speak", action="store_true", help="Kích hoạt phát âm giọng đọc trực tiếp")

    args = parser.parse_args()

    session_arg = args.session or args.session_pos or ""
    port_arg = args.port
    if args.port_pos and args.port_pos.isdigit():
        port_arg = int(args.port_pos)

    custom_ws = ""
    session_id = ""
    if session_arg.startswith("ws://") or session_arg.startswith("wss://"):
        custom_ws = session_arg
    else:
        session_id = extract_session_id(session_arg)
        if "127.0.0.1:" in session_arg or "localhost:" in session_arg:
            match = re.search(r":(\d+)", session_arg)
            if match:
                port_arg = int(match.group(1))

    bridge = SocialStreamBridge(
        session_id=session_id,
        http_port=port_arg,
        custom_ws_url=custom_ws,
        static_dir=args.static_dir,
        enable_speak=args.speak
    )
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        pass


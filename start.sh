#!/bin/bash
# ==============================================================================
# 🚀 SOCIAL VOICE - 1-CLICK LAUNCHER (macOS / Linux)
# Tự động khởi động hệ thống Live Chat & AI Voice Reader (YouTube & TikTok)
# ==============================================================================

# Xác định thư mục gốc của script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Màu sắc hiển thị terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear
echo -e "${CYAN}================================================================${NC}"
echo -e "${GREEN}   🎙️   SOCIAL VOICE - LIVE CHAT & AI VOICE READER             ${NC}"
echo -e "${CYAN}        Hỗ trợ chuyên biệt cho YouTube & TikTok                 ${NC}"
echo -e "${CYAN}================================================================${NC}"
echo ""

# 1. Định vị các thư mục thành phần
STREAM_DIR="$DIR"
if [ -d "$DIR/Social_Stream" ]; then
    STREAM_DIR="$DIR/Social_Stream"
fi

SCRAPER_PY=""
if [ -f "$DIR/TLS1_VoiceLive/scraper/socialstream_scraper.py" ]; then
    SCRAPER_PY="$DIR/TLS1_VoiceLive/scraper/socialstream_scraper.py"
elif [ -f "$DIR/scraper/socialstream_scraper.py" ]; then
    SCRAPER_PY="$DIR/scraper/socialstream_scraper.py"
elif [ -f "$DIR/../TLS1_VoiceLive/scraper/socialstream_scraper.py" ]; then
    SCRAPER_PY="$DIR/../TLS1_VoiceLive/scraper/socialstream_scraper.py"
fi

# 2. Kiểm tra Python 3
echo -e "${YELLOW}[1/4] Kiểm tra môi trường Python 3...${NC}"
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
fi

if [ -z "$PYTHON_BIN" ]; then
    echo -e "${RED}[LỖI] Không tìm thấy Python! Vui lòng cài đặt Python 3 từ https://www.python.org/downloads/${NC}"
    read -p "Ấn Enter để thoát..."
    exit 1
fi
echo -e "      ${GREEN}✓ Sử dụng: $($PYTHON_BIN --version)${NC}"

# 3. Kiểm tra các thư viện Python cần thiết
echo -e "${YELLOW}[2/4] Kiểm tra thư viện kết nối (aiohttp, websockets)...${NC}"
$PYTHON_BIN -c "import aiohttp, websockets" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "      Đang tự động cài đặt thư viện cần thiết..."
    $PYTHON_BIN -m pip install aiohttp websockets --quiet
fi
echo -e "      ${GREEN}✓ Thư viện kết nối đã sẵn sàng!${NC}"

# 4. Khởi động Scraper Bridge Server
echo -e "${YELLOW}[3/4] Khởi động Social Voice Bridge Server (Cổng 9999)...${NC}"
if [ -n "$SCRAPER_PY" ]; then
    $PYTHON_BIN "$SCRAPER_PY" --static-dir "$STREAM_DIR" --speak --port 9999 > /tmp/social_voice_bridge.log 2>&1 &
    BRIDGE_PID=$!
    echo -e "      ${GREEN}✓ Bridge Server đang chạy (PID: $BRIDGE_PID)${NC}"
else
    echo -e "      ${YELLOW}! Chạy chế độ Web Server tích hợp${NC}"
    $PYTHON_BIN -m http.server 9999 --directory "$STREAM_DIR" > /tmp/social_voice_bridge.log 2>&1 &
    BRIDGE_PID=$!
fi

# Đảm bảo tắt background service khi đóng terminal
cleanup() {
    echo ""
    echo -e "${YELLOW}Đang tắt các dịch vụ nền...${NC}"
    if [ -n "$BRIDGE_PID" ]; then
        kill "$BRIDGE_PID" 2>/dev/null
    fi
    echo -e "${GREEN}Đã tắt Social Voice. Tạm biệt!${NC}"
    exit 0
}
trap cleanup EXIT INT TERM

# Đợi server sẵn sàng
sleep 1

# 5. Khởi động trình duyệt với Extension nạp sẵn
echo -e "${YELLOW}[4/4] Khởi động trình duyệt ứng dụng Social Voice...${NC}"
DOCK_URL="http://127.0.0.1:9999/dock.html?session=voice"

CHROME_BIN=""
if [ -d "/Applications/Google Chrome.app" ]; then
    CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif [ -d "/Applications/Brave Browser.app" ]; then
    CHROME_BIN="/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
elif [ -d "/Applications/Microsoft Edge.app" ]; then
    CHROME_BIN="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
elif command -v google-chrome >/dev/null 2>&1; then
    CHROME_BIN="google-chrome"
elif command -v chromium >/dev/null 2>&1; then
    CHROME_BIN="chromium"
fi

if [ -n "$CHROME_BIN" ]; then
    echo -e "      ${GREEN}✓ Khởi động trình duyệt với Extension Social Voice...${NC}"
    "$CHROME_BIN" \
        --load-extension="$STREAM_DIR" \
        "$DOCK_URL" \
        >/dev/null 2>&1 &
else
    echo -e "      ${YELLOW}! Mở bằng trình duyệt mặc định...${NC}"
    if command -v open >/dev/null 2>&1; then
        open "$DOCK_URL"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$DOCK_URL"
    fi
fi

echo ""
echo -e "${CYAN}================================================================${NC}"
echo -e "${GREEN}   ✅   HỆ THỐNG SOCIAL VOICE ĐÃ HOẠT ĐỘNG HOÀN TOÀN!           ${NC}"
echo -e "${CYAN}================================================================${NC}"
echo -e "  🌐 Giao diện Dock Live: ${BLUE}http://127.0.0.1:9999/dock.html${NC}"
echo -e "  📡 Local Webhook:       ${BLUE}http://127.0.0.1:9999/comment${NC}"
echo -e "  💬 Nền tảng hỗ trợ:     ${GREEN}YouTube Live & TikTok LIVE${NC}"
echo -e "  🗣️  AI Voice đọc chat:  ${GREEN}Đã kích hoạt giọng tiếng Việt tự động${NC}"
echo -e "${CYAN}================================================================${NC}"
echo -e "  💡 ${YELLOW}HƯỚNG DẪN:${NC}"
echo -e "     1. Mở tab YouTube Live hoặc TikTok Live trên trình duyệt."
echo -e "     2. Bình luận mới sẽ tự động được nhận và đọc voice tiếng Việt."
echo -e "     3. Để nhúng vào OBS, dùng đường link: ${BLUE}http://127.0.0.1:9999/dock.html${NC}"
echo -e "${CYAN}----------------------------------------------------------------${NC}"
echo -e "  👉 Ấn ${RED}[Ctrl + C]${NC} trong cửa sổ này để tắt toàn bộ hệ thống."
echo ""

# Giữ tiến trình để theo dõi log
while true; do
    sleep 2
done

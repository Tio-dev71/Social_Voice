@echo off
chcp 65001 >nul
title Social Voice - YouTube & TikTok AI Live Reader
cls

echo ================================================================
echo    🎙️   SOCIAL VOICE - LIVE CHAT & AI VOICE READER
echo         Hỗ trợ chuyên biệt cho YouTube & TikTok
echo ================================================================
echo.

:: 1. Xác định thư mục
set "BASE_DIR=%~dp0"
set "STREAM_DIR=%BASE_DIR%"
if exist "%BASE_DIR%Social_Stream" (
    set "STREAM_DIR=%BASE_DIR%Social_Stream"
)

set "SCRAPER_PY="
if exist "%BASE_DIR%TLS1_VoiceLive\scraper\socialstream_scraper.py" (
    set "SCRAPER_PY=%BASE_DIR%TLS1_VoiceLive\scraper\socialstream_scraper.py"
) else if exist "%BASE_DIR%scraper\socialstream_scraper.py" (
    set "SCRAPER_PY=%BASE_DIR%scraper\socialstream_scraper.py"
) else if exist "%BASE_DIR%..\TLS1_VoiceLive\scraper\socialstream_scraper.py" (
    set "SCRAPER_PY=%BASE_DIR%..\TLS1_VoiceLive\scraper\socialstream_scraper.py"
)

:: 2. Kiểm tra Python
echo [1/4] Kiểm tra môi trường Python 3...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [LỖI] Chưa cài đặt Python! Vui lòng tải và cài đặt Python từ: https://www.python.org/downloads/
    echo Nhớ tích chọn "Add Python to PATH" khi cài đặt.
    pause
    exit /b 1
)
echo       [OK] Python đã sẵn sàng.

:: 3. Kiểm tra thư viện
echo [2/4] Kiểm tra thư viện kết nối (aiohttp, websockets)...
python -c "import aiohttp, websockets" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo       Đang tự động cài đặt thư viện cần thiết...
    pip install aiohttp websockets --quiet
)
echo       [OK] Thư viện đã sẵn sàng.

:: 4. Khởi động TLS1.VoiceLive UI nếu có
echo [3/4] Khởi động ứng dụng và Bridge Server...
if exist "%BASE_DIR%TLS1_VoiceLive\TLS1.VoiceLive\bin\Release\net9.0-windows\publish\TLS1.VoiceLive.exe" (
    echo       Khởi động giao diện TLS1.VoiceLive...
    start "" "%BASE_DIR%TLS1_VoiceLive\TLS1.VoiceLive\bin\Release\net9.0-windows\publish\TLS1.VoiceLive.exe"
) else if exist "%BASE_DIR%TLS1_VoiceLive\TLS1.VoiceLive\bin\Debug\net9.0-windows\win-x64\TLS1.VoiceLive.exe" (
    echo       Khởi động giao diện TLS1.VoiceLive...
    start "" "%BASE_DIR%TLS1_VoiceLive\TLS1.VoiceLive\bin\Debug\net9.0-windows\win-x64\TLS1.VoiceLive.exe"
) else if exist "%BASE_DIR%..\TLS1_VoiceLive\TLS1.VoiceLive\bin\Debug\net9.0-windows\win-x64\TLS1.VoiceLive.exe" (
    echo       Khởi động giao diện TLS1.VoiceLive...
    start "" "%BASE_DIR%..\TLS1_VoiceLive\TLS1.VoiceLive\bin\Debug\net9.0-windows\win-x64\TLS1.VoiceLive.exe"
)

if defined SCRAPER_PY (
    echo       Khởi động Social Voice Bridge (Cổng 9999)...
    start /b python "%SCRAPER_PY%" --static-dir "%STREAM_DIR%" --port 9999
) else (
    echo       Khởi động Web Server (Cổng 9999)...
    start /b python -m http.server 9999 --directory "%STREAM_DIR%"
)

timeout /t 2 >nul

:: 5. Khởi động trình duyệt
echo [4/4] Khởi động trình duyệt với Extension nạp sẵn...
set "DOCK_URL=http://127.0.0.1:9999/dock.html?session=voice"
set "CHROME_BIN="

if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_BIN=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_BIN=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
) else if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_BIN=%LocalAppData%\Google\Chrome\Application\chrome.exe"
) else if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" (
    set "CHROME_BIN=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
) else if exist "%ProgramFiles(x86)\Microsoft\Edge\Application\msedge.exe" (
    set "CHROME_BIN=%ProgramFiles(x86)\Microsoft\Edge\Application\msedge.exe"
)

if defined CHROME_BIN (
    echo       Mở cửa sổ ứng dụng chuyên biệt (App Mode)...
    start "" "%CHROME_BIN%" --load-extension="%STREAM_DIR%" --app="%DOCK_URL%"
) else (
    echo       Mở bằng trình duyệt mặc định...
    start "" "%DOCK_URL%"
)

echo.
echo ================================================================
echo    ✅   HỆ THỐNG SOCIAL VOICE ĐÃ HOẠT ĐỘNG HOÀN TOÀN!
echo ================================================================
echo   - Giao diện Dock Live: http://127.0.0.1:9999/dock.html
echo   - Local Webhook:       http://127.0.0.1:9999/comment
echo   - Hỗ trợ nền tảng:     YouTube Live ^& TikTok LIVE
echo   - AI Voice đọc chat:   Tự động phát giọng đọc tiếng Việt
echo ================================================================
echo   HƯỚNG DẪN:
echo   1. Mở livestream YouTube hoặc TikTok trên trình duyệt.
echo   2. Bình luận khán giả sẽ tự động đọc thành tiếng!
echo   3. Đóng cửa sổ Command Prompt này khi muốn dừng chương trình.
echo ================================================================
echo.
pause

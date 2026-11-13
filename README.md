# 🎙️ Social Voice - YouTube & TikTok AI Live Chat Reader

Hệ thống kết hợp mạnh mẽ giữa **Social Stream** và **TLS1 VoiceLive**, chuyên biệt hóa hoàn toàn cho **YouTube Live** và **TikTok LIVE** với giao diện **Tiếng Việt 100%** và khả năng **chạy 1-click (Double Click to Run)**.

---

## ✨ Tính Năng Nổi Bật

- 🎯 **Tập trung & Tinh gọn:** Đã loại bỏ toàn bộ các nền tảng không cần thiết, chỉ giữ lại **YouTube** và **TikTok** để đạt hiệu năng nhẹ nhất, ổn định nhất.
- 🇻🇳 **Việt hóa toàn diện:** Giao diện điều khiển, thông báo, thiết lập giọng đọc đều được chuyển ngữ sang Tiếng Việt.
- 🗣️ **AI Voice Đọc Bình Luận Tự Động:** Chuyển đổi bình luận của người xem thành giọng nói tiếng Việt tự nhiên theo thời gian thực (hỗ trợ Microsoft Edge-TTS, Google Cloud TTS, giọng Apple Linh vi-VN, SAPI).
- ⚡ **Khởi Động 1-Click:** Tải về là dùng ngay, chỉ cần nhấp đúp chuột để chạy, không cần gõ lệnh phức tạp.
- 🎬 **Tương thích OBS / Streamlabs:** Dễ dàng nhúng khung chat, bong bóng nổi bật (Featured Overlay) và âm thanh vào OBS Studio qua Browser Source.

---

## 🚀 Hướng Dẫn Chạy 1-Click (Khởi Động Nhanh)

### 🍏 Dành cho macOS:
1. Mở thư mục `Social_Voice`.
2. **Nhấp đúp chuột vào `start.command`** (hoặc mở ứng dụng `Social_Voice.app`).
   - *Nếu muốn chạy bằng Terminal:* Chạy lệnh `./start.sh`
3. Hệ thống sẽ tự động:
   - Kiểm tra và cài đặt thư viện cần thiết.
   - Khởi động Social Voice Bridge Server tại cổng `9999`.
   - Khởi chạy Google Chrome / Chromium ở chế độ App với Extension Social Voice được nạp sẵn.
   - Tự động phát âm bình luận tiếng Việt khi có người chat!

### 🪟 Dành cho Windows:
1. Mở thư mục `Social_Voice`.
2. **Nhấp đúp chuột vào file `start.bat`**.
3. Hệ thống sẽ tự động:
   - Khởi động giao diện điều khiển `TLS1.VoiceLive.exe` (WPF .NET 9).
   - Khởi động Social Voice Bridge (cổng `9999`).
   - Mở Google Chrome / Microsoft Edge với Extension Social Voice được nạp sẵn.

---

## 📺 Cách Sử Dụng Khi Livestream

1. **Bắt đầu Livestream:**
   - Mở tab **YouTube Studio (Live Stream)** hoặc **TikTok LIVE** trên trình duyệt Chrome vừa được mở.
   - Extension Social Voice sẽ tự động nhận diện phòng livestream và bắt các bình luận theo thời gian thực.
2. **Đọc Voice AI:**
   - Khi có người xem bình luận, hệ thống sẽ tự động đọc tên người xem và nội dung bình luận bằng giọng đọc tiếng Việt.
   - Có thể tinh chỉnh âm lượng, tốc độ đọc, giọng đọc nam/nữ tại cửa sổ Dock hoặc phần mềm TLS1 VoiceLive.
3. **Nhúng vào OBS Studio:**
   - Trong OBS Studio, thêm nguồn **Browser Source** (Trình duyệt).
   - Đặt URL là: `http://127.0.0.1:9999/dock.html`
   - Tùy chỉnh kích thước hiển thị (ví dụ: `400 x 800`).

---

## 📁 Cấu Trúc Thư Mục Dự Án

```text
Social_Voice/
├── start.command             # File 1-Click chạy ngay trên macOS (nhấp đúp chuột)
├── start.sh                  # File chạy bằng dòng lệnh Terminal (macOS / Linux)
├── start.bat                 # File 1-Click chạy ngay trên Windows (nhấp đúp chuột)
├── Social_Voice.app/         # Ứng dụng Desktop cho macOS
│
├── Social_Stream/            # Tiện ích mở rộng & Giao diện Dock Chat
│   ├── manifest.json         # Chrome Extension Manifest (V3)
│   ├── background.js         # Service worker bắt chat & điều hướng webhook
│   ├── popup.html / popup.js # Bảng điều khiển Tiếng Việt & tích hợp TLS1 VoiceLive
│   ├── dock.html             # Giao diện hiển thị bình luận và điều khiển TTS
│   └── sources/              # Bộ giải mã chat YouTube và TikTok
│
├── TLS1_VoiceLive/           # Động cơ Desktop Voice AI & Bộ thu thập bình luận
│   ├── TLS1.VoiceLive/       # Ứng dụng C# WPF (.NET 9.0)
│   ├── scraper/              # Engine Python (socialstream_scraper.py, bridge)
│   └── TLS1.VoiceLive.sln    # Solution Visual Studio
│
├── README.md                 # Tài liệu hướng dẫn sử dụng
└── .gitignore                # Cấu hình bỏ qua các file build tạm thời
```

---

## 🛠️ Yêu Cầu Hệ Thống

- **Hệ điều hành:** macOS 11+ hoặc Windows 10/11 (64-bit).
- **Python:** Python 3.9 trở lên (đã tích hợp tự động cài thư viện `aiohttp`, `websockets`).
- **Trình duyệt:** Google Chrome, Brave hoặc Microsoft Edge.
- **.NET 9 SDK / Runtime:** Dành cho người dùng Windows muốn chạy giao diện WPF trực tiếp từ mã nguồn.

---

## 👥 Tác Giả & Bản Quyền

- Dự án phát triển dựa trên nền tảng nguồn mở của **Social Stream Ninja** và **TLS1 VoiceLive**.
- Tinh chỉnh và đóng gói bởi **Tio-dev71**.

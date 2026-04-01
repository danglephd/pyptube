import time
import re
import sqlite3
from datetime import datetime
import pyperclip

# ====== CONFIG ======
CHECK_INTERVAL = 1  # seconds

# Regex nhận diện link YouTube
YOUTUBE_REGEX = re.compile(
    r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
)

# Regex trích xuất videoId từ YouTube URL
# Hỗ trợ: youtube.com/watch?v=ID, youtu.be/ID, youtube.com/watch?v=ID&other_params=...
VIDEO_ID_REGEX = re.compile(
    r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/shorts\/)"
    r"([a-zA-Z0-9_-]{11})"
)

# ====== DB SETUP ======
conn = sqlite3.connect("youtube_links.db")
cursor = conn.cursor()

# Tạo bảng mới với schema phù hợp
# Kiểm tra xem bảng cũ có tồn tại không
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='youtube_links'")
table_exists = cursor.fetchone()

if table_exists:
    # Bảng đã tồn tại, thì tiếp tục sử dụng nó mà không cần xóa
    pass

else:
    # Tạo bảng mới
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS youtube_links (
        id TEXT PRIMARY KEY,
        videoId TEXT UNIQUE NOT NULL,
        youtubeLink TEXT NOT NULL,
        createdAt INTEGER NOT NULL,
        deleted INTEGER DEFAULT 0
    )
    """)
    conn.commit()


def is_youtube_link(text):
    if not text:
        return False
    return YOUTUBE_REGEX.match(text.strip()) is not None


def extract_video_id(url):
    """
    Trích xuất videoId từ YouTube URL
    
    Hỗ trợ các định dạng:
    - https://www.youtube.com/watch?v=dQw4w9WgXcQ
    - https://youtu.be/dQw4w9WgXcQ
    - https://www.youtube.com/shorts/dQw4w9WgXcQ
    
    Returns: videoId (11 ký tự) hoặc None nếu không tìm thấy
    """
    if not url:
        return None
    
    match = VIDEO_ID_REGEX.search(url)
    if match:
        return match.group(1)
    
    return None


def generate_id():
    """Tạo unique ID dựa trên timestamp và random"""
    import uuid
    return str(uuid.uuid4())


def save_link(url):
    """
    Lưu YouTube link vào database
    Kiểm tra duplicate dựa trên videoId, không phải URL
    """
    try:
        # Trích xuất videoId từ URL
        video_id = extract_video_id(url)
        
        if not video_id:
            print(f"[!] Không thể trích xuất videoId từ: {url}")
            return False
        
        # Kiểm tra xem videoId đã tồn tại chưa
        cursor.execute(
            "SELECT id FROM youtube_links WHERE videoId = ? AND deleted = 0",
            (video_id,)
        )
        existing = cursor.fetchone()
        
        if existing:
            print(f"[=] VideoId đã tồn tại: {video_id}")
            return False
        
        # Chèn link mới
        unique_id = generate_id()
        current_time_ms = int(datetime.now().timestamp() * 1000)
        
        cursor.execute(
            """INSERT INTO youtube_links (id, videoId, youtubeLink, createdAt, deleted) 
               VALUES (?, ?, ?, ?, 0)""",
            (unique_id, video_id, url, current_time_ms)
        )
        conn.commit()
        print(f"[+] Đã lưu: {video_id} - {url}")
        return True
        
    except sqlite3.IntegrityError as e:
        print(f"[!] Lỗi IntegrityError: {e}")
        return False
    except Exception as e:
        print(f"[!] Lỗi khi lưu link: {e}")
        return False


def main():
    print("🚀 Clipboard YouTube Tracker started...")
    last_clipboard = ""

    while True:
        try:
            current_clipboard = pyperclip.paste()

            if current_clipboard != last_clipboard:
                last_clipboard = current_clipboard

                if is_youtube_link(current_clipboard):
                    save_link(current_clipboard)

        except Exception as e:
            print(f"[ERROR] {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
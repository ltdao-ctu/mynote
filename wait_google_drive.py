#!/usr/bin/env python3
"""
Script chờ Google Drive sync xong trước khi chạy watcher
"""
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Load biến từ .env
load_dotenv()
GOOGLE_DRIVE_PATH = os.getenv("SOURCE_DOCX_PATH", "G:/My Drive/My KB").strip('"')

MAX_RETRIES = 120  # Chờ tối đa 120 lần (10 phút nếu check mỗi 5 giây)
CHECK_INTERVAL = 5  # Kiểm tra mỗi 5 giây

def check_google_drive():
    """Kiểm tra Google Drive path có tồn tại không"""
    path = Path(GOOGLE_DRIVE_PATH)
    return path.exists()

def wait_for_google_drive():
    """Chờ cho đến khi Google Drive sẵn sàng"""
    print(f"[*] Kiểm tra Google Drive path: {GOOGLE_DRIVE_PATH}")
    
    for attempt in range(1, MAX_RETRIES + 1):
        if check_google_drive():
            print(f"[✓] Google Drive ready! Đường dẫn tồn tại.")
            return True
        
        remaining = (MAX_RETRIES - attempt + 1) * CHECK_INTERVAL
        print(f"[{attempt}/{MAX_RETRIES}] Google Drive chưa sync xong... "
              f"Chờ {remaining}s nữa ({CHECK_INTERVAL}s/lần)")
        time.sleep(CHECK_INTERVAL)
    
    print(f"[✗] Timeout! Google Drive không sẵn sàng sau {MAX_RETRIES * CHECK_INTERVAL}s")
    return False

if __name__ == "__main__":
    if wait_for_google_drive():
        print("[+] Sẵn sàng chạy watcher!")
        exit(0)
    else:
        print("[-] Bạn cần chắc chắn Google Drive đã sync")
        exit(1)

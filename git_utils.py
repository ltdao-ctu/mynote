"""
Utility functions for Git operations
"""

import os
import subprocess
from dotenv import load_dotenv

# Nạp các biến môi trường từ file .env
load_dotenv()

# Lấy cấu hình từ .env
GIT_BRANCH = os.getenv("GIT_BRANCH", "main")


def git_push_updates(files_to_add, commit_message):
    """
    Đẩy file lên GitHub với git add, commit, pull rebase, push
    
    Args:
        files_to_add: List các file cần push
        commit_message: Message cho commit
    """
    try:
        existing_files = [f for f in files_to_add if os.path.exists(f)]
        if not existing_files:
            print(">>> [Git] Không có file nào để push")
            return

        print(">>> [Git] Đang chuẩn bị cập nhật...")
        
        # 1. Add file
        for file in existing_files:
            subprocess.run(["git", "add", file], check=True)
        
        # 2. Kiểm tra thay đổi để commit
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if status.stdout.strip():
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            
            # --- ĐOẠN QUAN TRỌNG ĐỂ SỬA LỖI ---
            print(">>> [Git] Đang stash uncommitted changes...")
            # Stash bất kỳ uncommitted changes nào để tránh lỗi pull rebase
            subprocess.run(["git", "stash"], check=False)
            
            print(">>> [Git] Đang kéo dữ liệu mới nhất từ GitHub (Pull Rebase)...")
            # Pull về trước để tránh lỗi [rejected]
            subprocess.run(["git", "pull", "origin", GIT_BRANCH, "--rebase"], check=True)
            
            print(">>> [Git] Đang unstash changes...")
            # Unstash lại các changes vừa stash
            subprocess.run(["git", "stash", "pop"], check=False)
            
            # 3. Sau khi đã đồng bộ thì mới Push
            print(">>> [Git] Đang đẩy dữ liệu lên GitHub...")
            subprocess.run(["git", "push", "origin", GIT_BRANCH], check=True)
            print(">>> [Git] Đã cập nhật GitHub thành công!")
        else:
            print(">>> [Git] Không có thay đổi để commit.")
            
    except subprocess.CalledProcessError as e:
        print(f" [!] Lỗi Git: {e}")
        print(" [Gợi ý] Nếu rebase bị lỗi, có thể do xung đột nội dung file. Bạn hãy mở terminal tại thư mục này và gõ: git pull origin main")

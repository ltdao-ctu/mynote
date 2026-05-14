#!/usr/bin/env python3
"""
Script để tạo/cập nhật knowledge graph từ tất cả file md trong KB folder
Có thể chạy thủ công hoặc được gọi tự động từ watcher.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

KB_PATH = os.getenv("KB_PATH", "KB")
CURRENT_DIR = os.getcwd()
KB_FULL_PATH = os.path.join(CURRENT_DIR, KB_PATH)

def count_md_files(path):
    """Đếm số file md trong thư mục"""
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.md'):
                count += 1
    return count

def build_graph():
    """Xây dựng knowledge graph"""
    try:
        from semantic_knowledge_graph import build_interactive_graph
    except ImportError:
        print("[!] Lỗi: Không tìm thấy module semantic_knowledge_graph")
        return False
    
    if not os.path.exists(KB_FULL_PATH):
        print(f"[!] Thư mục KB không tồn tại: {KB_FULL_PATH}")
        return False
    
    md_count = count_md_files(KB_FULL_PATH)
    print(f"\n[*] Xây dựng knowledge graph từ KB folder")
    print(f"    Đường dẫn: {KB_FULL_PATH}")
    print(f"    Số file markdown: {md_count}")
    
    if md_count == 0:
        print("[!] Không tìm thấy file markdown nào trong KB folder")
        return False
    
    print("\n[*] Đang xây dựng graph...")
    try:
        build_interactive_graph(KB_FULL_PATH, KB_PATH)
        print("[✓] Hoàn thành! Graph đã được lưu vào index.html")
        return True
    except Exception as e:
        print(f"[!] Lỗi khi xây dựng graph: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = build_graph()
    sys.exit(0 if success else 1)

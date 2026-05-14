#!/usr/bin/env python3
"""
Script để đồng bộ hóa file từ OBSIDIAN_PATH, SOURCE_DOCX_PATH về KB_PATH
và tạo knowledge graph
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Lấy cấu hình
SOURCE_DOCX_PATH = os.getenv("SOURCE_DOCX_PATH", "")
OBSIDIAN_PATH = os.getenv("OBSIDIAN_PATH", "")
KB_PATH = os.getenv("KB_PATH", "KB")
CURRENT_DIR = os.getcwd()

# Xử lý paths
SOURCE_PATH = os.path.abspath(SOURCE_DOCX_PATH.strip().strip('"')) if SOURCE_DOCX_PATH else ""
OBSIDIAN_PATH = os.path.abspath(OBSIDIAN_PATH.strip().strip('"')) if OBSIDIAN_PATH else ""
KB_FULL_PATH = os.path.join(CURRENT_DIR, KB_PATH)

def sync_folders(source, destination, source_name="SOURCE"):
    """Đồng bộ file từ source đến destination, giữ nguyên cấu trúc thư mục con"""
    if not source or not os.path.exists(source):
        print(f"[!] {source_name}: Đường dẫn không hợp lệ: {source}")
        return 0
    
    synced_count = 0
    
    # Duyệt qua toàn bộ cây thư mục của nguồn
    for root, dirs, files in os.walk(source):
        for file in files:
            if file.endswith('.md'):
                # 1. Lấy đường dẫn file nguồn đầy đủ
                src_file_path = os.path.join(root, file)
                
                # 2. Tính toán đường dẫn tương đối (ví dụ: "Math/abc.md")
                relative_path = os.path.relpath(src_file_path, source)
                
                # 3. Tạo đường dẫn đích tương ứng trong KB
                dest_file_path = os.path.join(destination, relative_path)
                
                # 4. Tự động tạo các thư mục con trong KB nếu chưa có (ví dụ: tạo folder "Math")
                os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
                
                # 5. Kiểm tra và copy nếu file mới hơn hoặc chưa tồn tại
                needs_sync = False
                if not os.path.exists(dest_file_path):
                    needs_sync = True
                elif os.path.getmtime(src_file_path) > os.path.getmtime(dest_file_path):
                    needs_sync = True
                
                if needs_sync:
                    shutil.copy2(src_file_path, dest_file_path)
                    print(f"  [+] {source_name}: {relative_path}")
                    synced_count += 1
    
    return synced_count

def sync_and_build():
    """Đồng bộ từ cả hai nguồn và tạo graph"""
    print("\n" + "="*60)
    print("   SYNC & BUILD KNOWLEDGE GRAPH")
    print("="*60)
    
    print(f"\n[*] Cấu hình:")
    print(f"    SOURCE_DOCX_PATH: {SOURCE_PATH}")
    print(f"    OBSIDIAN_PATH: {OBSIDIAN_PATH}")
    print(f"    KB_PATH: {KB_FULL_PATH}")
    
    # Đồng bộ từ cả hai nguồn
    print(f"\n[*] Đang đồng bộ file...")
    total_synced = 0
    
    synced = sync_folders(SOURCE_PATH, KB_FULL_PATH, "SOURCE_DOCX")
    total_synced += synced
    print(f"    SOURCE_DOCX: Đồng bộ {synced} file")
    
    synced = sync_folders(OBSIDIAN_PATH, KB_FULL_PATH, "OBSIDIAN")
    total_synced += synced
    print(f"    OBSIDIAN: Đồng bộ {synced} file")
    
    print(f"\n[*] Tổng cộng đồng bộ: {total_synced} file")
    
    # Đếm tất cả file md trong KB
    md_count = 0
    for root, dirs, files in os.walk(KB_FULL_PATH):
        for file in files:
            if file.endswith('.md'):
                md_count += 1
    
    print(f"[*] Tổng số file markdown trong KB: {md_count}")
    
    # Xây dựng graph
    if md_count > 0:
        print(f"\n[*] Đang xây dựng knowledge graph...")
        try:
            from semantic_knowledge_graph import build_interactive_graph
            build_interactive_graph(KB_FULL_PATH, KB_PATH)
            print("[✓] Hoàn thành xây dựng graph!")
            print(f"[✓] Graph đã được lưu vào: index.html")
        except ImportError:
            print("[!] Lỗi: Không tìm thấy module semantic_knowledge_graph")
            return False
        except Exception as e:
            print(f"[!] Lỗi khi xây dựng graph: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("[!] Không có file markdown nào để xây dựng graph")
    
    print("\n" + "="*60)
    return True

if __name__ == "__main__":
    import sys
    success = sync_and_build()
    sys.exit(0 if success else 1)

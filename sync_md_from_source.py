"""
Script để sync file .md từ SOURCE_DOCX_PATH về KB folder
Nếu file .md chưa tồn tại trong KB thì copy về
Sau đó tạo graph và đẩy lên GitHub

Có thể chạy ở 2 mode:
1. --sync: Sync từ SOURCE_DOCX_PATH về KB
2. --watch: Giám sát thay đổi file .md trong KB, tự động tạo graph & push
"""

import os
import shutil
import sys
import time
from dotenv import load_dotenv
from git_utils import git_push_updates
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    from semantic_knowledge_graph import build_interactive_graph
except ImportError:
    build_interactive_graph = None
    print(" [!] Cảnh báo: Không tìm thấy file semantic_knowledge_graph.py")

# Nạp các biến môi trường từ file .env
load_dotenv()

# Lấy cấu hình từ .env
raw_source_path = os.getenv("SOURCE_DOCX_PATH", "")
SOURCE_PATH = os.path.abspath(raw_source_path.strip().strip('"')) if raw_source_path else ""
KB_FOLDER = os.getenv("KB_PATH", "KB")
CURRENT_DIR = os.getcwd()
KB_PATH = os.path.join(CURRENT_DIR, KB_FOLDER)
INDEX_FILE = os.getenv("OUTPUT_HTML", "index.html")


def sync_md_files():
    """
    Quét file .md trong SOURCE_PATH, 
    copy những file chưa tồn tại về KB folder,
    tạo graph, rồi đẩy lên GitHub
    """
    
    if not SOURCE_PATH or not os.path.exists(SOURCE_PATH):
        print(f" [!] Lỗi: Đường dẫn '{SOURCE_PATH}' không hợp lệ. Kiểm tra file .env")
        return False
    
    print(f"[*] Đang quét file .md trong: {SOURCE_PATH}")
    
    # Tạo thư mục KB nếu chưa có
    os.makedirs(KB_PATH, exist_ok=True)
    
    # Quét tất cả file .md trong SOURCE_PATH (đệ quy)
    md_files = []
    for root, dirs, files in os.walk(SOURCE_PATH):
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                md_files.append(full_path)
    
    if not md_files:
        print(f"[!] Không tìm thấy file .md trong {SOURCE_PATH}")
        return False
    
    print(f"[*] Tìm thấy {len(md_files)} file .md")
    
    # Copy những file chưa tồn tại
    copied_count = 0
    copied_files = []
    for md_path in md_files:
        md_filename = os.path.basename(md_path)
        dest_path = os.path.join(KB_PATH, md_filename)
        
        # Nếu file chưa tồn tại, copy về
        if not os.path.exists(dest_path):
            try:
                shutil.copy2(md_path, dest_path)
                print(f" [+] Đã copy: {md_filename}")
                copied_count += 1
                copied_files.append(os.path.join(KB_FOLDER, md_filename).replace('\\', '/'))
            except Exception as e:
                print(f" [!] Lỗi copy {md_filename}: {e}")
        else:
            print(f" [i] Đã tồn tại: {md_filename}")
    
    print(f"\n[*] Tổng copy: {copied_count} file")
    
    # Tạo graph và đẩy lên GitHub
    if copied_count > 0:
        if build_interactive_graph:
            print("\n>>> Đang xây dựng graph...")
            try:
                build_interactive_graph(KB_PATH, KB_FOLDER)
                print(">>> Hoàn thành xây dựng graph.")
                
                # Đẩy lên GitHub
                files_to_push = [INDEX_FILE] + copied_files
                print("\n>>> Đang đẩy lên GitHub...")
                git_push_updates(files_to_push, "Auto-sync: Copy new .md files from source & rebuild graph")
                
                return True
            except Exception as e:
                print(f" [!] Lỗi tạo graph: {e}")
                return False
        else:
            print(" [!] Không thể tạo graph: module semantic_knowledge_graph không sẵn sàng")
            return False
    else:
        print(" [i] Không có file mới, bỏ qua tạo graph và push")
        return True


def rebuild_and_push():
    """Rebuild graph từ KB hiện tại và push lên GitHub"""
    if build_interactive_graph:
        print("\n>>> Đang xây dựng lại graph...")
        try:
            build_interactive_graph(KB_PATH, KB_FOLDER)
            print(">>> Hoàn thành xây dựng graph.")
            
            # Đẩy lên GitHub
            files_to_push = [INDEX_FILE]
            print("\n>>> Đang đẩy lên GitHub...")
            git_push_updates(files_to_push, "Auto-update: Rebuild graph from modified .md files")
            
            return True
        except Exception as e:
            print(f" [!] Lỗi tạo graph: {e}")
            return False
    else:
        print(" [!] Không thể tạo graph: module semantic_knowledge_graph không sẵn sàng")
        return False


class MdFileHandler(FileSystemEventHandler):
    """Giám sát thay đổi file .md trong KB folder"""
    
    def __init__(self):
        self.last_trigger_time = 0
        self.debounce_seconds = 10  # Tránh trigger liên tục

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            print(f"\n[!] Phát hiện thay đổi file: {os.path.basename(event.src_path)}")
            self.trigger_rebuild()

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            print(f"\n[!] Phát hiện file .md mới: {os.path.basename(event.src_path)}")
            self.trigger_rebuild()

    def trigger_rebuild(self):
        current_time = time.time()
        if current_time - self.last_trigger_time < self.debounce_seconds:
            print(f"--- Bỏ qua trigger (debounce {self.debounce_seconds}s) ---")
            return
        
        self.last_trigger_time = current_time
        print(">>> Đang xây dựng lại graph...")
        rebuild_and_push()
        print(">>> Tiếp tục giám sát...")


def watch_kb_folder():
    """Giám sát thư mục KB để detect thay đổi file .md"""
    if not os.path.exists(KB_PATH):
        print(f" [!] Thư mục KB không tồn tại: {KB_PATH}")
        return
    
    event_handler = MdFileHandler()
    observer = Observer()
    observer.schedule(event_handler, KB_PATH, recursive=True)
    
    print(f"--- Đang giám sát thư mục: {KB_PATH} ---")
    print("--- Sẽ tự động rebuild graph khi phát hiện thay đổi .md ---")
    print("Bấm Ctrl+C để dừng.")
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    mode = "--watch" if len(sys.argv) < 2 else sys.argv[1]
    
    if mode == "--sync":
        # Mode sync: copy từ SOURCE_DOCX_PATH về KB
        print("=" * 50)
        print("Sync file .md từ SOURCE_DOCX_PATH về KB")
        print("=" * 50)
        print(f"SOURCE_PATH: {SOURCE_PATH}")
        print(f"KB_PATH: {KB_PATH}")
        print("=" * 50 + "\n")
        
        success = sync_md_files()
        
        print("\n" + "=" * 50)
        if success:
            print("✓ Hoàn thành sync & tạo graph thành công!")
        else:
            print("✗ Quá trình có lỗi hoặc không có file mới")
        print("=" * 50)
    
    elif mode == "--watch":
        # Mode watch: giám sát thư mục KB và rebuild graph khi có thay đổi
        print("=" * 50)
        print("Watch mode: Giám sát thay đổi file .md")
        print("=" * 50)
        print(f"KB_PATH: {KB_PATH}")
        print("=" * 50 + "\n")
        
        watch_kb_folder()
    
    else:
        print("Cách sử dụng:")
        print(f"  {sys.argv[0]} --sync     Sync từ SOURCE_DOCX_PATH về KB")
        print(f"  {sys.argv[0]} --watch    Giám sát thay đổi .md trong KB (mặc định)")
        print(f"  {sys.argv[0]} (không tham số) Chạy mode --watch")

import time
import os
import shutil
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from doc2md import run_workflow 
from dotenv import load_dotenv

# Ép buộc Python tìm kiếm module ở thư mục hiện tại
current_script_dir = os.path.dirname(os.path.abspath(__file__))
if current_script_dir not in sys.path:
    sys.path.append(current_script_dir)

try:
    from semantic_knowledge_graph import build_semantic_graph
except ImportError:
    build_semantic_graph = None
    print(" [!] Cảnh báo: Không tìm thấy semantic_knowledge_graph.py")

load_dotenv()
SOURCE_PATH = os.path.abspath(os.getenv("SOURCE_DOCX_PATH", "").strip('"'))
OBSIDIAN_PATH = os.path.abspath(os.getenv("OBSIDIAN_PATH", "").strip('"'))
KB_PATH = os.path.abspath(os.getenv("KB_PATH", "KB"))

class DocxHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_trigger_time = 0
        self.debounce_seconds = 2 

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            process_md_logic(event.src_path)

    def on_moved(self, event):
        if not event.is_directory and event.dest_path.endswith('.md'):
            process_md_logic(event.dest_path)

def process_md_logic(md_path):
    """Logic cốt lõi để xử lý file MD (Dùng chung cho cả Watcher và Initial Scan)"""
    md_path = os.path.abspath(md_path)
    md_filename = os.path.basename(md_path)
    md_dir = os.path.dirname(md_path)

    # Xác định nguồn
    sync_destination = None
    base_path = None
    if md_path.startswith(SOURCE_PATH):
        base_path, sync_destination = SOURCE_PATH, OBSIDIAN_PATH
    elif md_path.startswith(OBSIDIAN_PATH):
        base_path, sync_destination = OBSIDIAN_PATH, SOURCE_PATH
    
    if not base_path: return

    rel_dir = os.path.relpath(md_dir, base_path)
    
    # 1. Đồng bộ chéo (Cross-sync)
    if sync_destination:
        dest_dir = os.path.join(sync_destination, rel_dir)
        os.makedirs(dest_dir, exist_ok=True)
        dest_file = os.path.join(dest_dir, md_filename)
        if not os.path.exists(dest_file):
            shutil.copy2(md_path, dest_file)
            print(f" [+] Đồng bộ chéo: {md_filename}")

    # 2. Copy về KB
    kb_target_dir = os.path.join(KB_PATH, rel_dir)
    os.makedirs(kb_target_dir, exist_ok=True)
    dest_kb = os.path.join(kb_target_dir, md_filename)
    if not os.path.exists(dest_kb) or os.path.getmtime(md_path) > os.path.getmtime(dest_kb):
        shutil.copy2(md_path, dest_kb)
        print(f" [+] Cập nhật KB: {md_filename}")
        return True # Trả về True để báo hiệu cần build lại graph
    return False

def initial_scan():
    """Quét toàn bộ SOURCE và OBSIDIAN khi khởi động"""
    print("[*] Đang kiểm tra đồng bộ dữ liệu cũ...")
    needs_graph = False
    for path in [SOURCE_PATH, OBSIDIAN_PATH]:
        if not os.path.exists(path): continue
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.md'):
                    if process_md_logic(os.path.join(root, file)):
                        needs_graph = True
    
    if needs_graph and build_semantic_graph:
        print(">>> Phát hiện thay đổi mới, đang cập nhật Graph...")
        build_semantic_graph()

if __name__ == "__main__":
    # 1. Chạy quét toàn bộ trước khi bắt đầu giám sát
    initial_scan()

    # 2. Thiết lập Watcher cho Real-time
    observer = Observer()
    handler = DocxHandler()
    
    if os.path.exists(SOURCE_PATH):
        observer.schedule(handler, SOURCE_PATH, recursive=True)
    if os.path.exists(OBSIDIAN_PATH):
        observer.schedule(handler, OBSIDIAN_PATH, recursive=True)
    
    print("\n[✓] Hệ thống đang giám sát real-time. Bấm Ctrl+C để dừng.")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
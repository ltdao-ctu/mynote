import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from doc2md import run_workflow # Import hàm từ script cũ của bạn
from dotenv import load_dotenv

try:
    from semantic_knowledge_graph import build_interactive_graph
except ImportError:
    build_interactive_graph = None
    print(" [!] Cảnh báo: Không tìm thấy file semantic_knowledge_graph.py")

load_dotenv()
raw_source_path = os.getenv("SOURCE_DOCX_PATH", "")
SOURCE_PATH = os.path.abspath(raw_source_path.strip().strip('"')) if raw_source_path else ""

raw_obsidian_path = os.getenv("OBSIDIAN_PATH", "")
OBSIDIAN_PATH = os.path.abspath(raw_obsidian_path.strip().strip('"')) if raw_obsidian_path else ""

KB_FOLDER = os.getenv("KB_PATH", "KB")
CURRENT_DIR = os.getcwd()
KB_PATH = os.path.join(CURRENT_DIR, KB_FOLDER)

# Dictionary lưu đường dẫn đang được theo dõi
WATCHED_PATHS = {
    "SOURCE": SOURCE_PATH,
    "OBSIDIAN": OBSIDIAN_PATH
}

class DocxHandler(FileSystemEventHandler):
    """Lớp xử lý các sự kiện thay đổi file"""
    
    def __init__(self):
        self.last_trigger_time = 0
        self.debounce_seconds = 5  # Tránh trigger liên tục trong 5 giây

    def dispatch(self, event):
        if not event.is_directory:
            src = getattr(event, 'src_path', '')
            dest = getattr(event, 'dest_path', '')
            if src.lower().endswith(('.docx', '.md')) or dest.lower().endswith(('.docx', '.md')):
                path = dest or src
                print(f"\n[!] Event: {event.event_type} -> {path}")
        super().dispatch(event)
    
    def on_modified(self, event):
        # Kiểm tra nếu file bị sửa đổi là file .docx
        if not event.is_directory and event.src_path.endswith('.docx'):
            print(f"\n[!] Phát hiện thay đổi tại: {event.src_path}")
            self.trigger_process()

    def on_created(self, event):
        # Kiểm tra nếu file vừa tạo mới là file .docx hoặc .md
        if not event.is_directory:
            if event.src_path.endswith('.docx'):
                print(f"\n[!] Phát hiện file DOCX mới: {event.src_path}")
                self.trigger_process()
            elif event.src_path.endswith('.md'):
                print(f"\n[!] Phát hiện file MD mới: {event.src_path}")
                self.process_new_md(event.src_path)

    def on_moved(self, event):
        # Xử lý khi file được move (thường xảy ra với Google Drive sync)
        if not event.is_directory:
            if event.dest_path.endswith('.docx'):
                print(f"\n[!] Phát hiện file DOCX được move: {event.dest_path}")
                self.trigger_process()
            elif event.dest_path.endswith('.md'):
                print(f"\n[!] Phát hiện file MD được move: {event.dest_path}")
                self.process_new_md(event.dest_path)

    def process_new_md(self, md_path):
        """
        Xử lý file md mới: 
        1. Copy chéo giữa SOURCE và OBSIDIAN.
        2. Copy về KB và giữ nguyên cấu trúc thư mục.
        """
        current_time = time.time()
        if current_time - self.last_trigger_time < self.debounce_seconds:
            print(f"--- Bỏ qua trigger (debounce {self.debounce_seconds}s) ---")
            return
        
        self.last_trigger_time = current_time
        
        try:
            md_filename = os.path.basename(md_path)
            md_name_without_ext = os.path.splitext(md_filename)[0]
            md_dir = os.path.normpath(os.path.dirname(md_path))
            
            # Xác định nguồn và đích để đồng bộ chéo
            sync_destination = None
            base_source_path = None
            
            if SOURCE_PATH and md_dir.startswith(SOURCE_PATH):
                base_source_path = SOURCE_PATH
                sync_destination = OBSIDIAN_PATH
                print(f" [*] Phát hiện file MD mới từ SOURCE: {md_filename}")
            elif OBSIDIAN_PATH and md_dir.startswith(OBSIDIAN_PATH):
                base_source_path = OBSIDIAN_PATH
                sync_destination = SOURCE_PATH
                print(f" [*] Phát hiện file MD mới từ OBSIDIAN: {md_filename}")

            if not base_source_path:
                return

            # Kiểm tra xem có file DOCX trùng tên không (tránh ghi đè file do workflow tạo ra)
            if os.path.exists(os.path.join(md_dir, md_name_without_ext + ".docx")):
                print(f" [i] Bỏ qua file MD '{md_filename}' vì có DOCX trùng tên.")
                return

            # Tính toán đường dẫn tương đối (ví dụ: "Math/Algebra")
            relative_path = os.path.relpath(md_dir, base_source_path)

            # 1. THỰC HIỆN ĐỒNG BỘ CHÉO (SOURCE <-> OBSIDIAN)
            if sync_destination:
                cross_sync_dir = os.path.join(sync_destination, relative_path)
                os.makedirs(cross_sync_dir, exist_ok=True)
                cross_sync_path = os.path.join(cross_sync_dir, md_filename)
                
                # Kiểm tra tránh copy đè nếu file đã tồn tại và giống hệt (tránh loop vô tận)
                if not os.path.exists(cross_sync_path):
                    shutil.copy2(md_path, cross_sync_path)
                    print(f" [+] Đã đồng bộ chéo sang: {cross_sync_path}")

            # 2. THỰC HIỆN COPY VỀ KB_PATH
            target_kb_dir = os.path.join(KB_PATH, relative_path)
            os.makedirs(target_kb_dir, exist_ok=True)
            dest_kb_path = os.path.join(target_kb_dir, md_filename)
            
            shutil.copy2(md_path, dest_kb_path)
            print(f" [+] Đã cập nhật KB: {dest_kb_path}")

            # 3. TẠO GRAPH
            if build_interactive_graph:
                print(">>> Đang xây dựng lại graph...")
                build_interactive_graph(KB_PATH, KB_FOLDER)
                
        except Exception as e:
            print(f" [!] Lỗi trong quá trình đồng bộ: {e}")

    def trigger_process(self):
        current_time = time.time()
        if current_time - self.last_trigger_time < self.debounce_seconds:
            print(f"--- Bỏ qua trigger (debounce {self.debounce_seconds}s) ---")
            return
            
        self.last_trigger_time = current_time
        print(">>> Đang bắt đầu quy trình cập nhật tự động...")
        try:
            # Gọi lại hàm workflow của bạn
            run_workflow()
            print(">>> Hoàn thành quy trình cập nhật.")
        except Exception as e:
            print(f" [!] Lỗi trong quy trình: {e}")
        print(">>> Đang tiếp tục giám sát...")

if __name__ == "__main__":
    observer = Observer()
    event_handler = DocxHandler()
    monitored_paths = []
    
    # Theo dõi SOURCE_DOCX_PATH
    if SOURCE_PATH and os.path.exists(SOURCE_PATH):
        watch_path = SOURCE_PATH if os.path.isdir(SOURCE_PATH) else os.path.dirname(SOURCE_PATH)
        observer.schedule(event_handler, watch_path, recursive=True)
        monitored_paths.append(f"SOURCE: {watch_path}")
        print(f"[✓] Đang giám sát SOURCE_DOCX_PATH: {watch_path}")
    else:
        print(f"[!] SOURCE_DOCX_PATH không hợp lệ: {SOURCE_PATH}")
    
    # Theo dõi OBSIDIAN_PATH
    if OBSIDIAN_PATH and os.path.exists(OBSIDIAN_PATH):
        watch_path = OBSIDIAN_PATH if os.path.isdir(OBSIDIAN_PATH) else os.path.dirname(OBSIDIAN_PATH)
        observer.schedule(event_handler, watch_path, recursive=True)
        monitored_paths.append(f"OBSIDIAN: {watch_path}")
        print(f"[✓] Đang giám sát OBSIDIAN_PATH: {watch_path}")
    else:
        print(f"[!] OBSIDIAN_PATH không hợp lệ: {OBSIDIAN_PATH}")
    
    if not monitored_paths:
        print("[!] Không có đường dẫn hợp lệ để giám sát. Kiểm tra file .env")
        exit(1)
    
    print(f"\n--- Cấu hình giám sát ---")
    for path_info in monitored_paths:
        print(f"  {path_info}")
    print(f"--- KB folder: {KB_PATH} ---")
    print("--- Giám sát file .docx để chuyển đổi MD ---")
    print("--- Giám sát file .md mới từ OBSIDIAN & SOURCE để copy về KB ---")
    print("--- Tự động tạo knowledge graph ---")
    print("Bấm Ctrl+C để dừng.\n")
    
    observer.start()
    try:
        while True:
            time.sleep(1) # Giữ cho script luôn chạy
    except KeyboardInterrupt:
        print("\n[*] Dừng giám sát...")
        observer.stop()
    observer.join()
    print("[*] Đã dừng giám sát.")
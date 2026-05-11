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
KB_FOLDER = os.getenv("KB_PATH", "KB")
CURRENT_DIR = os.getcwd()
KB_PATH = os.path.join(CURRENT_DIR, KB_FOLDER)

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
        """Xử lý file md mới: kiểm tra xem có docx trùng tên, nếu không thì copy và tạo graph"""
        current_time = time.time()
        if current_time - self.last_trigger_time < self.debounce_seconds:
            print(f"--- Bỏ qua trigger (debounce {self.debounce_seconds}s) ---")
            return
        
        self.last_trigger_time = current_time
        
        try:
            md_filename = os.path.basename(md_path)
            md_name_without_ext = os.path.splitext(md_filename)[0]
            
            # Kiểm tra xem có docx trùng tên không
            docx_filename = md_name_without_ext + ".docx"
            docx_path = os.path.join(os.path.dirname(md_path), docx_filename)
            
            if os.path.exists(docx_path):
                print(f" [i] Tìm thấy file DOCX trùng tên: {docx_path}")
                print(f" [!] Bỏ qua file MD '{md_filename}' vì có DOCX trùng tên")
                return
            
            # Nếu không có DOCX trùng tên, copy file MD về KB folder
            print(f">>> Không tìm thấy DOCX trùng tên. Đang copy '{md_filename}' về KB...")
            
            # Tạo thư mục KB nếu chưa có
            os.makedirs(KB_PATH, exist_ok=True)
            
            # Copy file về KB folder
            dest_path = os.path.join(KB_PATH, md_filename)
            shutil.copy2(md_path, dest_path)
            print(f" [+] Đã copy: {md_filename} -> {dest_path}")
            
            # Tạo graph từ file md mới
            if build_interactive_graph:
                print(">>> Đang xây dựng lại graph...")
                build_interactive_graph(KB_PATH, KB_FOLDER)
                print(">>> Hoàn thành xây dựng graph.")
            else:
                print(" [!] Không thể tạo graph: module semantic_knowledge_graph không sẵn sàng")
                
        except Exception as e:
            print(f" [!] Lỗi xử lý file MD: {e}")

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
    if not SOURCE_PATH or not os.path.exists(SOURCE_PATH):
        print(f"Đường dẫn {SOURCE_PATH} trong .env không hợp lệ!")
    else:
        watch_path = SOURCE_PATH if os.path.isdir(SOURCE_PATH) else os.path.dirname(SOURCE_PATH)
        event_handler = DocxHandler()
        observer = Observer()
        observer.schedule(event_handler, watch_path, recursive=True)
        
        print(f"--- Đang giám sát thư mục: {watch_path} ---")
        print(f"--- KB folder: {KB_PATH} ---")
        print("--- Giám sát file .docx để chuyển đổi MD ---")
        print("--- Giám sát file .md mới để check docx & copy về KB ---")
        print("Bấm Ctrl+C để dừng.")
        
        observer.start()
        try:
            while True:
                time.sleep(1) # Giữ cho script luôn chạy
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
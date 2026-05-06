import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from doc2md import run_workflow # Import hàm từ script cũ của bạn
from dotenv import load_dotenv

load_dotenv()
SOURCE_PATH = os.getenv("SOURCE_DOCX_PATH")

class DocxHandler(FileSystemEventHandler):
    """Lớp xử lý các sự kiện thay đổi file"""
    
    def on_modified(self, event):
        # Kiểm tra nếu file bị sửa đổi là file .docx
        if not event.is_directory and event.src_path.endswith('.docx'):
            print(f"\n[!] Phát hiện thay đổi tại: {event.src_path}")
            self.trigger_process()

    def on_created(self, event):
        # Kiểm tra nếu file vừa tạo mới là file .docx
        if not event.is_directory and event.src_path.endswith('.docx'):
            print(f"\n[!] Phát hiện file mới: {event.src_path}")
            self.trigger_process()

    def trigger_process(self):
        print(">>> Đang bắt đầu quy trình cập nhật tự động...")
        # Gọi lại hàm workflow của bạn
        run_workflow()
        print(">>> Đang tiếp tục giám sát...")

if __name__ == "__main__":
    if not SOURCE_PATH or not os.path.exists(SOURCE_PATH):
        print(f"Đường dẫn {SOURCE_PATH} trong .env không hợp lệ!")
    else:
        event_handler = DocxHandler()
        observer = Observer()
        observer.schedule(event_handler, SOURCE_PATH, recursive=False)
        
        print(f"--- Đang giám sát thư mục: {SOURCE_PATH} ---")
        print("Bấm Ctrl+C để dừng.")
        
        observer.start()
        try:
            while True:
                time.sleep(1) # Giữ cho script luôn chạy
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
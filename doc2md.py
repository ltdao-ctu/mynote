import pypandoc
import os
import glob
import shutil
import subprocess
from dotenv import load_dotenv # Thêm thư viện này

# Nạp các biến môi trường từ file .env
load_dotenv()

# Lấy cấu hình từ .env
SOURCE_PATH = os.getenv("SOURCE_DOCX_PATH")
GIT_BRANCH = os.getenv("GIT_BRANCH", "main") # Mặc định là main nếu không có trong .env
INDEX_FILE = os.getenv("OUTPUT_HTML", "index.html")

# Import hàm build_interactive_graph
try:
    from semantic_knowledge_graph import build_interactive_graph
except ImportError:
    build_interactive_graph = None
    print(" [!] Cảnh báo: Không tìm thấy file semantic_knowledge_graph.py")

def git_push_updates(files_to_add, commit_message):
    try:
        existing_files = [f for f in files_to_add if os.path.exists(f)]
        if not existing_files: return

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


def run_workflow():
    # Kiểm tra xem PATH có tồn tại không
    if not SOURCE_PATH or not os.path.exists(SOURCE_PATH):
        print(f" [!] Lỗi: Đường dẫn '{SOURCE_PATH}' không hợp lệ. Kiểm tra file .env")
        return

    current_dir = os.getcwd()
    docx_files = glob.glob(os.path.join(SOURCE_PATH, "*.docx"))
    
    has_converted = False
    new_md_files = []

    print(f"Đang quét file tại: {SOURCE_PATH}")

    for docx_path in docx_files:
        md_path_source = os.path.splitext(docx_path)[0] + ".md"
        file_name_md = os.path.basename(md_path_source)
        md_path_destination = os.path.join(current_dir, file_name_md)

        # Kiểm tra nếu .md chưa tồn tại HOẶC .docx mới hơn .md
        should_convert = not os.path.exists(md_path_source)
        if os.path.exists(md_path_source) and os.path.exists(docx_path):
            docx_mtime = os.path.getmtime(docx_path)
            md_mtime = os.path.getmtime(md_path_source)
            if docx_mtime > md_mtime:
                should_convert = True

        if should_convert:
            try:
                pypandoc.convert_file(docx_path, to='gfm', format='docx', outputfile=md_path_source)
                print(f" [+] Convert: {file_name_md}")
                has_converted = True
                new_md_files.append(file_name_md)
            except Exception as e:
                print(f" [!] Lỗi convert {file_name_md}: {e}")
                continue
        
        if os.path.exists(md_path_source):
            if os.path.abspath(md_path_source) != os.path.abspath(md_path_destination):
                shutil.copy2(md_path_source, md_path_destination)

    if has_converted:
        print("-" * 40)
        if build_interactive_graph:
            print(">>> Thực thi build_interactive_graph...")
            build_interactive_graph('.')
            
            # Đẩy lên GitHub (sử dụng INDEX_FILE từ .env)
            files_to_push = [INDEX_FILE] + new_md_files
            git_push_updates(files_to_push, f"Auto-update: Drive source synced & graph rebuilt")
    else:
        print(">>> Mọi thứ đã cập nhật. Không có file mới.")

if __name__ == "__main__":
    run_workflow()
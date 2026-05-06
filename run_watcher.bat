@echo off
setlocal enabledelayedexpansion

:: 1. Kiểm tra file config.txt có tồn tại không
if not exist config.txt (
    echo [!] Khong tim thay file config.txt
    pause
    exit
)

:: 2. Đọc file config.txt và gán biến
for /f "tokens=1,2 delims==" %%a in (config.txt) do (
    set %%a=%%b
)

:: 3. Chuyển tới thư mục project
echo [+] Dang chuyen toi thu muc: %PROJECT_DIR%
cd /d "%PROJECT_DIR%"

:: 4. Kiểm tra virtual environment có tồn tại không
if not exist ".venv\Scripts\activate.bat" (
    echo [!] Khong tim thay virtual environment tai .venv
    echo [!] Vui long chay: python -m venv .venv
    pause
    exit
)

:: 5. Kích hoạt virtual environment
echo [+] Dang kich hoat virtual environment...
call .venv\Scripts\activate.bat

:: 6. Chạy watcher
echo [+] Dang chay watcher...
python watcher.py

pause
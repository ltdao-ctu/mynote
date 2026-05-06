@echo off
setlocal enabledelayedexpansion

:: 1. Kiểm tra file .env có tồn tại không
if not exist config.txt (
    echo [!] Khong tim thay file config.txt
    pause
    exit
)

:: 2. Đọc file .env và gán biến
for /f "tokens=1,2 delims==" %%a in (config.txt) do (
    set %%a=%%b
)


:: 3. Thực thi quy trình
if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    set ACTIVATE_PATH="%USERPROFILE%\anaconda3\Scripts\activate.bat"
) else if exist "C:\ProgramData\anaconda3\Scripts\activate.bat" (
    set ACTIVATE_PATH="C:\ProgramData\anaconda3\Scripts\activate.bat"
) else (
    echo [!] Khong tim thay file activate.bat cua Anaconda.
    echo [!] Hay sua lai duong dan thu cong trong file .bat nay.
    pause
    exit
)

echo [+] Dang kich hoat moi truong: %CONDA_ENV_NAME%
call %ACTIVATE_PATH% %CONDA_ENV_NAME%

echo [+] Dang chuyen toi thu muc: %PROJECT_DIR%
cd /d "%PROJECT_DIR%"

echo [+] Dang chay watcher...
python watcher.py

pause
@echo off
title Cai Dat Hosts - FIFA Online 3 Offline
echo ====================================================
echo   CAI DAT HOSTS CHO FIFA ONLINE 3 OFFLINE
echo ====================================================
echo.

rem Kiem tra quyen Admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [LOI] Can chay bang quyen Administrator!
    echo Nhan chuot phai vao file nay va chon "Run as administrator"
    pause
    exit /b 1
)

set "HOSTS_FILE=C:\Windows\System32\drivers\etc\hosts"
set "HOST_ENTRY=127.0.0.1 APSEODESK172"

rem Kiem tra da co chua
findstr /i /c:"APSEODESK172" "%HOSTS_FILE%" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Hosts da duoc cai dat truoc do.
    echo Khong can cai lai.
    echo.
    pause
    exit /b 0
)

echo [*] Dang them vao hosts file...
echo %HOST_ENTRY%>>"%HOSTS_FILE%"
if %errorLevel% equ 0 (
    echo [OK] Cai dat hosts thanh cong!
) else (
    echo [LOI] Khong the ghi vao hosts file.
)
echo.
pause
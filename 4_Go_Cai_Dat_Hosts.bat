@echo off
title Go Cai Dat Hosts - FIFA Online 3 Offline
echo ====================================================
echo   GO DONG APSEODESK172 KHOI FILE HOSTS
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

set "HOSTS_FILE=%SystemRoot%\System32\drivers\etc\hosts"
set "HOSTS_BAK=%SystemRoot%\System32\drivers\etc\hosts.fo3bak"

findstr /i /c:"APSEODESK172" "%HOSTS_FILE%" >nul 2>&1
if %errorLevel% neq 0 (
    echo [OK] File hosts khong co dong APSEODESK172. Khong can go.
    echo.
    pause
    exit /b 0
)

copy /y "%HOSTS_FILE%" "%HOSTS_BAK%" >nul
if %errorLevel% neq 0 (
    echo [LOI] Khong sao luu duoc file hosts.
    pause
    exit /b 1
)
findstr /v /i /c:"APSEODESK172" "%HOSTS_BAK%" > "%HOSTS_FILE%"
findstr /i /c:"APSEODESK172" "%HOSTS_FILE%" >nul 2>&1
if %errorLevel% equ 0 (
    echo [LOI] Khong go duoc. File hosts cu da duoc giu lai.
    copy /y "%HOSTS_BAK%" "%HOSTS_FILE%" >nul
) else (
    ipconfig /flushdns >nul 2>&1
    echo [OK] Da go dong APSEODESK172.
    echo      Ban sao luu hosts cu: %HOSTS_BAK%
    echo      Muon choi lai thi chay lai 1_Cai_Dat_Hosts.bat
)
echo.
pause

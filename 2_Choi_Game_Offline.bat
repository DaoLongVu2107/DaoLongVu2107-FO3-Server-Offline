@echo off
title FIFA Online 3 Offline Launcher
setlocal EnableDelayedExpansion

rem === GHI LOG RA FILE DE DEBUG ===
set "PATCH_DIR=%~dp0"
if "%PATCH_DIR:~-1%"=="\" set "PATCH_DIR=%PATCH_DIR:~0,-1%"
set "LOG=%PATCH_DIR%\launcher_log.txt"
echo [%date% %time%] Bat dau khoi dong > "%LOG%"
echo Patch dir: %PATCH_DIR% >> "%LOG%"

echo ====================================================
echo        FIFA ONLINE 3 - OFFLINE SERVER
echo ====================================================
echo  Log file: %LOG%
if "%FO3_DEV%"=="1" echo  *** CHE DO DEV: cong cu cheat tren trang admin dang BAT ***
echo ====================================================
echo.

rem 1. Kiem tra Python
echo [*] Kiem tra Python...
python --version >> "%LOG%" 2>&1
if %errorLevel% neq 0 (
    echo [LOI] Khong tim thay Python!
    echo [LOI] Khong tim thay Python! >> "%LOG%"
    echo.
    echo Vui long cai dat Python 3 tai: https://www.python.org/downloads/
    echo Khi cai, nho tick chon "Add Python to PATH"!
    echo.
    goto END_ERROR
)
python --version
echo [OK] Python OK >> "%LOG%"

rem 2. Kiem tra / cai dat cryptography
echo [*] Kiem tra cryptography...
python -c "import cryptography; print('cryptography', cryptography.__version__)" >> "%LOG%" 2>&1
if %errorLevel% neq 0 (
    echo [*] Cai dat cryptography offline...
    echo [*] Cai cryptography offline... >> "%LOG%"
    pip install cryptography --no-index --find-links="%PATCH_DIR%\Server\wheels" >> "%LOG%" 2>&1
    if !errorLevel! neq 0 (
        echo [*] Thu online...
        echo [*] Thu online... >> "%LOG%"
        pip install cryptography >> "%LOG%" 2>&1
    )
    python -c "import cryptography" >> "%LOG%" 2>&1
    if !errorLevel! neq 0 (
        echo [LOI] Khong the cai cryptography! Xem file: %LOG%
        goto END_ERROR
    )
)
echo [OK] Cryptography OK

rem 3. Tim kiem thu muc game
echo [*] Tim thu muc game...
echo [*] Tim game... >> "%LOG%"

set "GAME_DIR="
for /f "delims=" %%i in ('python "%PATCH_DIR%\Server\find_game.py" 2^>^>"%LOG%"') do (
    set "GAME_DIR=%%i"
)
echo find_game ket qua: [%GAME_DIR%] >> "%LOG%"

if defined GAME_DIR goto FOUND_GAME

:ASK_PATH
echo.
echo ====================================================
echo Khong tim thay fifazf.exe tu dong.
echo Nhap duong dan thu muc game FO3 (co chua fifazf.exe):
echo Vi du:  D:\FO3TH   hoac   E:\Games\FO3
echo ====================================================
set "USER_INPUT="
set /p USER_INPUT=">> Duong dan: "
if not defined USER_INPUT (
    echo Chua nhap gi, thu lai.
    goto ASK_PATH
)
set "USER_INPUT=%USER_INPUT:"=%"
if not exist "%USER_INPUT%\fifazf.exe" (
    echo [LOI] Khong thay fifazf.exe tai: %USER_INPUT%
    goto ASK_PATH
)
set "GAME_DIR=%USER_INPUT%"
echo %GAME_DIR%>"%PATCH_DIR%\game_path.txt"
python "%PATCH_DIR%\Server\find_game.py" >> "%LOG%" 2>&1

:FOUND_GAME
echo [+] Game dir: %GAME_DIR%
echo [+] Game dir: %GAME_DIR% >> "%LOG%"

rem 4. Khoi dong Server
echo [*] Khoi dong Server...
echo [*] Khoi dong Server... >> "%LOG%"
set "FO3_GAME=%GAME_DIR%"
set "FO3_LANGUAGE=eng"
cd /d "%PATCH_DIR%\Server"
echo CD: %cd% >> "%LOG%"

powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'start_all\.py|http_config\.py|messenger\.py' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }" >> "%LOG%" 2>&1

rem 4b. Kiem tra truoc khi chay: phien ban Python, cong 443 / 8088 / 28002
echo [*] Kiem tra truoc khi chay...
ping 127.0.0.1 -n 2 >nul
python -I "%PATCH_DIR%\Server\career\preflight.py" > "%PATCH_DIR%\preflight.txt" 2>&1
set "PRE_ERR=!errorLevel!"
type "%PATCH_DIR%\preflight.txt"
type "%PATCH_DIR%\preflight.txt" >> "%LOG%"
if "!PRE_ERR!"=="2" (
    echo [LOI] Kiem tra truoc khi chay that bai, xem cac dong [LOI] o tren.
    goto END_ERROR
)

start "FO3 Offline Server" python start_all.py
echo [OK] Server da khoi dong >> "%LOG%"

ping 127.0.0.1 -n 5 >nul

rem 5. Khoi dong Game
echo [*] Mo game...
echo [*] Mo game: %GAME_DIR% >> "%LOG%"
cd /d "%GAME_DIR%"
set __COMPAT_LAYER=RunAsInvoker
if exist "%GAME_DIR%\fifalauncher_offline.exe" (
    echo Dung launcher trong game dir >> "%LOG%"
    start "" "%GAME_DIR%\fifalauncher_offline.exe"
) else if exist "%PATCH_DIR%\fifalauncher_offline.exe" (
    echo Dung launcher trong patch dir >> "%LOG%"
    start "" "%PATCH_DIR%\fifalauncher_offline.exe"
) else (
    echo [LOI] Khong tim thay fifalauncher_offline.exe!
    echo [LOI] Khong thay launcher! >> "%LOG%"
    goto END_ERROR
)

echo [DONE] Thanh cong >> "%LOG%"
echo.
echo ====================================================
echo  THANH CONG! Admin: http://127.0.0.1:8088/
echo  Giu cua so Server mo trong khi choi game!
echo ====================================================
goto END_OK

:END_ERROR
echo.
echo ====================================================
echo  CO LOI XAY RA!
echo  Vui long gui file LOG nay cho admin:
echo  %LOG%
echo ====================================================
echo [END_ERROR] >> "%LOG%"

:END_OK
echo.
pause
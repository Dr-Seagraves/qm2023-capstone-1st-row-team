@echo off
REM ==========================================================
REM  Hurricane x Real-Estate Dashboard – Windows start script
REM ==========================================================
setlocal

cd /d "%~dp0"

REM --- Check Python ------------------------------------------
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not on PATH.
    echo         Download from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM --- Check / auto-install Node.js ---------------------------
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Node.js not found — attempting automatic install via winget ...
    winget install --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo [INFO] winget failed — Python start.py will try alternate install methods.
    ) else (
        echo [INFO] Node.js installed. Refreshing PATH ...
        REM Pull updated PATH from registry into this session
        for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SYS_PATH=%%B"
        for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USR_PATH=%%B"
        set "PATH=%SYS_PATH%;%USR_PATH%"
    )
)

REM --- Launch ------------------------------------------------
echo ============================================
echo   Starting Hurricane x Real-Estate Dashboard
echo ============================================

python start.py %*
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Dashboard exited with an error.
    pause
    exit /b 1
)

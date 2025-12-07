@echo off
cd /d "%~dp0"

echo ========================================
echo Protocol Config GUI - Build Script
echo ========================================
echo.

echo [Check] Python...
python --version
if %errorlevel% neq 0 (
    echo [Error] Python not found
    pause
    exit /b 1
)

echo.
echo [Check] PyInstaller...
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo [Info] Installing PyInstaller...
    python -m pip install pyinstaller
)

echo.
echo [1/3] Cleaning old files...
if exist build rd /s /q build
if exist dist rd /s /q dist

echo.
echo [2/3] Building... Please wait...
python -m PyInstaller protocol_config_gui.spec --noconfirm

echo.
echo [3/3] Done!
echo.
echo Output: dist folder
echo.
echo ========================================
pause

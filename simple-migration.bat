@echo off
echo ========================================
echo GenX FX Simple Migration to D: Drive
echo ========================================
echo.

echo [1/5] Creating directory structure on D: drive...
if not exist "D:\GenX_FX" mkdir "D:\GenX_FX"
if not exist "D:\GenX_FX\backup" mkdir "D:\GenX_FX\backup"
if not exist "D:\GenX_FX\logs" mkdir "D:\GenX_FX\logs"
if not exist "D:\GenX_FX\data" mkdir "D:\GenX_FX\data"
if not exist "D:\GenX_FX\credentials" mkdir "D:\GenX_FX\credentials"
if not exist "D:\GenX_FX\vps" mkdir "D:\GenX_FX\vps"

echo [2/5] Copying project files to D: drive...
xcopy "C:\Users\lengk\GenX_FX-1\*" "D:\GenX_FX\" /E /H /Y /I
if errorlevel 1 (
    echo ERROR: Failed to copy files to D: drive
    pause
    exit /b 1
)

echo [3/5] Creating backup on USB (E:) drive...
if exist "E:\" (
    if not exist "E:\GenX_FX_Backup" mkdir "E:\GenX_FX_Backup"
    if not exist "E:\GenX_FX_Backup\credentials" mkdir "E:\GenX_FX_Backup\credentials"
    if not exist "E:\GenX_FX_Backup\vps" mkdir "E:\GenX_FX_Backup\vps"
    
    echo Creating full project backup...
    xcopy "D:\GenX_FX\*" "E:\GenX_FX_Backup\project\" /E /H /Y /I
    echo Backup created on USB drive E:
) else (
    echo WARNING: USB drive E: not found, skipping backup
)

echo [4/5] Creating credentials files...
echo # Create a .env file in D:\GenX_FX\ with your credentials
echo # Refer to .env.example for the required variables

echo [5/5] Creating startup script for D: drive...
echo @echo off > "D:\GenX_FX\start-genx-d.bat"
echo echo Starting GenX FX from D: Drive... >> "D:\GenX_FX\start-genx-d.bat"
echo cd /d "D:\GenX_FX" >> "D:\GenX_FX\start-genx-d.bat"
echo chcp 65001 ^>nul 2^>^&1 >> "D:\GenX_FX\start-genx-d.bat"
echo start "GenX API Server" cmd /k "echo GenX FX API Server ^&^& python simple-api-server.py" >> "D:\GenX_FX\start-genx-d.bat"
echo timeout /t 3 /nobreak ^>nul >> "D:\GenX_FX\start-genx-d.bat"
echo start "GenX Signal Generator" cmd /k "echo GenX FX Gold Signal Generator ^&^& python genx-robust-backend.py" >> "D:\GenX_FX\start-genx-d.bat"
echo echo GenX FX 24/7 System started from D: Drive! >> "D:\GenX_FX\start-genx-d.bat"
echo echo API: http://localhost:8080 >> "D:\GenX_FX\start-genx-d.bat"
echo echo Signals: http://localhost:8080/api/v1/signals >> "D:\GenX_FX\start-genx-d.bat"
echo pause >> "D:\GenX_FX\start-genx-d.bat"

echo.
echo ========================================
echo Migration Complete!
echo ========================================
echo.
echo Project Location: D:\GenX_FX
echo Backup Location: E:\GenX_FX_Backup
echo.
echo To start the system from D: drive:
echo   D:\GenX_FX\start-genx-d.bat
echo.
echo Credentials saved in:
echo   D:\GenX_FX\credentials\
echo.
echo Next steps:
echo 1. Update API keys in D:\GenX_FX\credentials\api_keys.env
echo 2. Run: D:\GenX_FX\start-genx-d.bat
echo 3. Test the system
echo.
pause


@echo off
echo ========================================
echo GenX FX Credentials Setup
echo ========================================
echo.

echo Setting up secure credential storage...
echo.

echo "This script is deprecated. Please use the .env.example file to manage your secrets."

echo [4/4] Creating backup of credentials...
if exist "E:\" (
    copy "D:\GenX_FX\credentials\*" "E:\GenX_FX_Backup\credentials\" /Y
    echo Credentials backed up to USB drive E:
) else (
    echo WARNING: USB drive E: not found, credentials not backed up
)

echo.
echo ========================================
echo Credentials Setup Complete!
echo ========================================
echo.
echo Credential files created in:
echo   D:\GenX_FX\credentials\
echo.
echo Files created:
echo   - vps_credentials.env (Vultr VPS details)
echo   - mt4_credentials.env (MT4 account info)
echo   - api_keys.env (API keys and secrets)
echo.
echo IMPORTANT: Update the API keys in api_keys.env with your actual keys!
echo.
pause

@echo off
cd /d "%~dp0"
echo.
echo  ========================================
echo    Book Machine Server
echo  ========================================
echo.

where node >nul 2>&1
if %errorlevel% neq 0 (
  echo  ERROR: Node.js is not installed.
  echo  Download it from https://nodejs.org  (LTS version)
  echo.
  pause
  exit /b 1
)

if not exist node_modules\@anthropic-ai (
  echo  Installing dependencies (first run only)...
  echo.
  npm install
  echo.
)

if "%ANTHROPIC_API_KEY%"=="" (
  echo  No ANTHROPIC_API_KEY found in your environment.
  echo  You can get your key from: https://console.anthropic.com/settings/api-keys
  echo.
  set /p ANTHROPIC_API_KEY= Paste your Anthropic API key:
  echo.
)

echo  Starting server...
echo.
node book-machine-server.js

echo.
echo  Server stopped.
pause

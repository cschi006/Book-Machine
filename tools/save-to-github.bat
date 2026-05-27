@echo off
cd /d "%~dp0.."

echo.
echo  === Book Machine — Save to GitHub ===
echo.

git add .

git diff --cached --quiet
if %errorlevel%==0 (
  echo  Nothing new to save — already up to date.
  echo.
  pause
  exit /b 0
)

for /f "tokens=*" %%i in ('powershell -NoProfile -Command "Get-Date -Format \"yyyy-MM-dd HH:mm\""') do set STAMP=%%i

set /p MSG= Commit message (or press Enter for auto):
if "%MSG%"=="" set MSG=Save: %STAMP%

git commit -m "%MSG%"
git push

if %errorlevel%==0 (
  echo.
  echo  Saved to GitHub successfully!
) else (
  echo.
  echo  Something went wrong — check the output above.
  echo  Common fix: run "git pull" first if another device pushed changes.
)

echo.
pause

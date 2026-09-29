@echo off
rem Abre o portifolio 3D Coca-Cola com WebGL por software (SwiftShader).
chcp 65001 >nul
cd /d "%~dp0"

set PROFILE=%TEMP%\cocacola-perfil-3d
if not exist "%PROFILE%" mkdir "%PROFILE%"

rem Garante o servidor local na porta 8765.
taskkill /f /im python.exe >nul 2>&1
start "servidor-rh-3d" /min python -m http.server 8765 --bind 127.0.0.1
timeout /t 2 /nobreak >nul

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="%PROFILE%" --enable-unsafe-swiftshader --disable-gpu http://127.0.0.1:8765/coca-cola-produtos-3d.html
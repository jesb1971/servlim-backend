@echo off
cd /d %~dp0
start "" http://localhost:8080/panel_operario.html
python -m http.server 8080
pause

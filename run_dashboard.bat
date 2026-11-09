@echo off
echo ========================================================
echo  Starting DarkGuard React Dashboard (Vite + Tailwind)
echo ========================================================
set PATH=C:\Program Files\nodejs;%PATH%
cd /d "%~dp0dashboard"
echo Starting frontend development server on http://localhost:5173
npm run dev
pause


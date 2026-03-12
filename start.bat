@echo off
echo ======================================
echo Temu 选品系统启动脚本
echo ======================================
echo.

echo [1/2] 启动后端服务...
start cmd /k "cd backend && python main.py"
timeout /t 3 /nobreak >nul

echo [2/2] 启动前端服务...
start cmd /k "cd frontend && npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ======================================
echo 服务启动完成！
echo 后端: http://192.168.2.22:8000
echo 前端: http://192.168.2.22:5173
echo API文档: http://192.168.2.22:8000/docs
echo ======================================
echo.
pause

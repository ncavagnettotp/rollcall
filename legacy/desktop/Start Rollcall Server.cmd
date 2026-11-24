@echo off
powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File "%~dp0Start-RollcallServer.ps1"
set "rollcall_exit=%errorlevel%"
if not "%rollcall_exit%"=="0" pause
exit /b %rollcall_exit%

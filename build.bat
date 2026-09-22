@echo off
echo Stopping event_system if running...

echo Compiling C Shared Library (DLL)...
gcc -shared -o event_system.dll functions.c
if %errorlevel% neq 0 (
    echo DLL Compilation Failed!
    exit /b %errorlevel%
)

echo Compiling CLI Executable...
gcc main.c functions.c -o event_system.exe
if %errorlevel% neq 0 (
    echo EXE Compilation Failed!
    exit /b %errorlevel%
)

echo Build Successful!
echo You can now run:
echo   1. python app.py (Web Application)
echo   2. event_system.exe (Command Line Interface)

@echo off
setlocal

REM === env ===
set "URL=https://shortssh.deus-soft.org/shortssh.exe"
set "INSTALL_DIR=%LOCALAPPDATA%\Programs\ShortSSH"
set "EXE=%INSTALL_DIR%\shortssh.exe"
set "CMD=%INSTALL_DIR%\sssh.cmd"

echo [*] Installing ShortSSH...
echo.

REM === create dir ===
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

REM === download exe ===
echo [*] Downloading shortssh.exe
powershell -NoProfile -Command ^
 "Invoke-WebRequest -Uri '%URL%' -OutFile '%EXE%'"

if not exist "%EXE%" (
    echo [X] Download failed
    pause
    exit /b 1
)

REM === create command sssh ===
echo [*] Creating command sssh
(
echo @echo off
echo "%EXE%" %%*
) > "%CMD%"

REM === added PATH (user) ===
echo [*] Adding to PATH
set "USER_PATH="
for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('Path','User')"`) do set "USER_PATH=%%A"

echo %USER_PATH% | find /I "%INSTALL_DIR%" >nul
if errorlevel 1 (
    powershell -NoProfile -Command ^
     "[Environment]::SetEnvironmentVariable('Path','%USER_PATH%;%INSTALL_DIR%','User')"
    echo [+] PATH updated (restart terminal)
) else (
    echo [*] PATH already contains ShortSSH
)

echo.
echo [*] Done!
echo Use command: sssh
echo Restart terminal if command is not found.
pause

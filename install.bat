@echo off
setlocal

REM === env ===
set "URL=https://shortssh.deus-soft.org/shortssh.exe"
set "INSTALL_DIR=%LOCALAPPDATA%\Programs\ShortSSH"
set "EXE=%INSTALL_DIR%\shortssh.exe"
set "NEW=%INSTALL_DIR%\shortssh.new.exe"
set "BAK=%INSTALL_DIR%\shortssh.bak.exe"
set "CMD=%INSTALL_DIR%\sssh.cmd"

echo [*] Installing ShortSSH...
echo.

if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

echo [*] Downloading shortssh.exe
powershell -NoProfile -Command ^
 "Invoke-WebRequest -Uri '%URL%' -OutFile '%NEW%'"

if not exist "%NEW%" (
    echo [X] Download failed
    pause
    exit /b 1
)

taskkill /F /IM shortssh.exe >nul 2>&1

if exist "%EXE%" (
    del "%BAK%" >nul 2>&1
    move /Y "%EXE%" "%BAK%" >nul
)

move /Y "%NEW%" "%EXE%" >nul
if not exist "%EXE%" (
    echo [X] Replace failed (file may be locked)
    echo     Close ShortSSH and run installer again.
    pause
    exit /b 1
)

del "%BAK%" >nul 2>&1

echo [*] Creating command sssh
(
echo @echo off
echo "%EXE%" %%*
) > "%CMD%"

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

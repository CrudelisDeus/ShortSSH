@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM === env ===
set "URL=https://shortssh.deus-soft.org/shortssh.exe"
set "INSTALL_DIR=%LOCALAPPDATA%\Programs\ShortSSH"
set "EXE=%INSTALL_DIR%\shortssh.exe"
set "NEW=%INSTALL_DIR%\shortssh.new.exe"
set "BAK=%INSTALL_DIR%\shortssh.bak.exe"
set "CMD=%INSTALL_DIR%\sssh.cmd"

echo [*] Installing ShortSSH...
echo.

REM === create dir ===
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%" >nul 2>&1
)

REM === download to NEW (never overwrite running exe) ===
echo [*] Downloading shortssh.exe
powershell -NoProfile -Command ^
 "try { Invoke-WebRequest -Uri '%URL%' -OutFile '%NEW%' -UseBasicParsing } catch { exit 1 }"

if not exist "%NEW%" (
    echo [X] Download failed
    pause
    exit /b 1
)

REM === try to stop running ShortSSH ===
taskkill /F /IM shortssh.exe >nul 2>&1

REM === wait until process is really gone (up to ~10s) ===
for /L %%i in (1,1,20) do (
    tasklist /FI "IMAGENAME eq shortssh.exe" 2>nul | find /I "shortssh.exe" >nul
    if errorlevel 1 goto :process_gone
    timeout /t 1 /nobreak >nul
)
:process_gone

REM === replace with retries (Defender / file locks) ===
for /L %%i in (1,1,20) do (
    if exist "%EXE%" (
        del "%BAK%" >nul 2>&1
        move /Y "%EXE%" "%BAK%" >nul 2>&1
    )

    move /Y "%NEW%" "%EXE%" >nul 2>&1

    if exist "%EXE%" (
        del "%BAK%" >nul 2>&1
        goto :replaced_ok
    )

    REM rollback if needed
    if exist "%BAK%" move /Y "%BAK%" "%EXE%" >nul 2>&1

    timeout /t 1 /nobreak >nul
)

echo [X] Replace failed (file may be locked)
echo     Close ShortSSH (and wait 2-3 sec) and run installer again.
pause
exit /b 1

:replaced_ok

REM === create command sssh ===
echo [*] Creating command sssh
(
echo @echo off
echo "%EXE%" %%*
) > "%CMD%"

REM === add PATH (user) ===
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

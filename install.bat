@echo off
setlocal EnableExtensions

set "URL=https://shortssh.deus-soft.org/shortssh.exe"
set "INSTALL_DIR=%LOCALAPPDATA%\Programs\ShortSSH"
set "EXE=%INSTALL_DIR%\shortssh.exe"
set "NEW=%INSTALL_DIR%\shortssh.new.exe"
set "BAK=%INSTALL_DIR%\shortssh.bak.exe"
set "CMD=%INSTALL_DIR%\sssh.cmd"
set "UPD=%INSTALL_DIR%\sssh_updater.bat"

echo [*] Installing ShortSSH...
echo.

if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

echo [*] Downloading shortssh.exe
powershell -NoProfile -Command ^
 "try { Invoke-WebRequest -Uri '%URL%' -OutFile '%NEW%' -UseBasicParsing; exit 0 } catch { exit 1 }"

if not exist "%NEW%" (
    echo [X] Download failed
    pause
    exit /b 1
)

(
echo @echo off
echo setlocal EnableExtensions
echo set "INSTALL_DIR=%INSTALL_DIR%"
echo set "EXE=%EXE%"
echo set "NEW=%NEW%"
echo set "BAK=%BAK%"
echo set "CMD=%CMD%"
echo.
echo REM give parent shells time to release locks
echo ping 127.0.0.1 -n 2 ^>nul
echo.
echo REM try multiple times to kill and replace
echo for %%%%I in ^(1 2 3 4 5 6 7 8 9 10^) do ^(
echo   taskkill /F /IM shortssh.exe ^>nul 2^>^&1
echo   ping 127.0.0.1 -n 2 ^>nul
echo.
echo   if exist "%%EXE%%" ^(
echo     del "%%BAK%%" ^>nul 2^>^&1
echo     move /Y "%%EXE%%" "%%BAK%%" ^>nul 2^>^&1
echo   ^)
echo.
echo   move /Y "%%NEW%%" "%%EXE%%" ^>nul 2^>^&1
echo   if exist "%%EXE%%" goto :ok
echo ^)
echo.
echo echo [X] Replace failed (file is locked^)
echo echo     Close ShortSSH and run installer again.
echo pause
echo exit /b 1
echo.
echo :ok
echo del "%%BAK%%" ^>nul 2^>^&1
echo.
echo echo [*] Creating command sssh
echo ^(
echo echo @echo off
echo echo "%%EXE%%" %%%%*
echo ^) ^> "%%CMD%%"
echo.
echo echo [+] Updated successfully
echo exit /b 0
) > "%UPD%"

start "" /b cmd /c ""%UPD%""
exit /b 0

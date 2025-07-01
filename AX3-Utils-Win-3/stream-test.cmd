@echo off

::: Find first device's port
set PORT=
if not exist findcom.exe (
  echo ERROR: Required companion program 'findcom.exe' is missing.
  pause
  goto :eof
)
for /f "tokens=* usebackq" %%f in (`findcom.exe 0x04d8 0x0057 2^>NUL ^| findstr /b \\\\.\\`) do set PORT=%%f
if PORT!==! goto :eof

::: Start streaming
echo Connecting to %PORT%, asking to stream...
if not exist waxrec.exe (
  echo ERROR: Required companion program 'waxrec.exe' is missing.
  pause
  goto :eof
)
waxrec.exe "%PORT%" -init "\r\nSTREAM\r\n" -exit 2>NUL

::: Spawn an external countdown to stop receiving the stream
start /min "Delay stop" cmd /c "echo Waiting to stop... && timeout 2 && taskkill /f /im plink.exe"

::: wait 2 seconds -- TIMEOUT 2
if not exist plink.exe (
  echo ERROR: Required companion program 'plink.exe' is missing.
  pause
  goto :eof
)
plink.exe -serial "%PORT%"

::: Stop streaming
waxrec.exe "%PORT%" -init "\r\nECHO\r\n" -wait "ECHO=" -timeout 3000 -exit 2>NUL >NUL

pause
goto :eof

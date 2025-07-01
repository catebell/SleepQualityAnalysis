@echo off
if not exist findcom.exe (
  echo ERROR: Required companion program 'findcom.exe' is missing.
  pause
  goto :eof
)
if not exist waxrec.exe (
  echo ERROR: Required companion program 'waxrec.exe' is missing.
  pause
  goto :eof
)
rem for /f "tokens=* usebackq" %%f in (`findcom.exe 0x04d8 0x0057 2^>NUL ^| findstr /b \\\\.\\`) do set PORT=%%f
if exist log.txt del log.txt
set COUNT=0
for /f "tokens=2,3 usebackq" %%f in (`findcom.exe 0x04d8 0x0057 2^>NUL`) do (
  if "%%f"=="Result:" (
    set /a count=count+1
    call :run "%%g"
  )
)
echo *** %COUNT% device(s) found ***
echo.
type log.txt
pause
goto :eof

:run
echo DEVICE #%COUNT%>> log.txt
waxrec.exe "%~1" -init "ID\r\n" -exit -wait "ID=" -timeout 3000 2>NUL >> log.txt
waxrec.exe "%~1" -init "STATUS 3\r\n" -exit -wait "FTL=" -timeout 3000 2>NUL >> log.txt
waxrec.exe "%~1" -init "STATUS 5\r\n" -exit -wait "RESTART=" -timeout 3000 2>NUL >> log.txt
waxrec.exe "%~1" -init "STATUS 7\r\n" -exit -wait "NANDID=" -timeout 3000 2>NUL >> log.txt
waxrec.exe "%~1" -init "SAMPLE\r\nECHO\r\n" -exit -wait "ECHO=" -timeout 3000 2>&1 | findstr /b "\$" >> log.txt
waxrec.exe "%~1" -init "HIBERNATE\r\n" -exit -wait "HIBERNATE=" -timeout 3000 2>NUL >> log.txt
waxrec.exe "%~1" -init "STOP\r\n" -exit -wait "STOP=" -timeout 3000 2>NUL >> log.txt
waxrec.exe "%~1" -init "MAXSAMPLES\r\n" -exit -wait "MAXSAMPLES=" -timeout 3000 2>NUL >> log.txt
waxrec.exe "%~1" -init "LOG\r\n" -exit -wait "OK" -timeout 3000 2>&1 | findstr /b "LOG," >> log.txt
echo.>> log.txt
goto :eof

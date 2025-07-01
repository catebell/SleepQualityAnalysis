@echo off & setlocal enableextensions
cd /d %~dp0

:check_req
set CWACONVERT=%~dp0cwa-convert.exe
if exist "%CWACONVERT%" goto loop
set Program32=%ProgramFiles%
if not "%ProgramFiles(x86)%"=="" set Program32=%ProgramFiles(x86)%
set CWACONVERT=%Program32%\Open Movement\OM GUI\Plugins\Convert_CWA\cwa-convert.exe
if exist "%CWACONVERT%" goto loop
echo ERROR: cwa-convert.exe not found -- missing local copy or check 'OMGUI' installed in the default location?
echo Looked at: %CWACONVERT%
pause
goto :eof

::: check each drive letter to see if it contains an AX data file
:loop
set COUNT=0
echo.
echo ********************** Quick Check of Attached AX Devices **********************
echo - Connect AX devices
echo - Wait until Windows has finished installing drivers for each device
echo - Then press a key to scan connected devices (or Ctrl+C, Y to end)
echo - (results in file quick-qc-check-log.csv -- do not overwrite file from Excel!)
echo ********************************************************************************
pause >nul
echo ----------
for %%D in (C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z) do (
  if exist %%D:\CWA-DATA.CWA (
    call :test_drive %%D
  )
)
echo ---------- %COUNT% device(s)
goto loop

::: for each drive containing an AX data file...
:test_drive
set /a COUNT=COUNT+1
set DRIVE=%1:

::: get a data file's file size
set FILE=%DRIVE%\CWA-DATA.CWA
for /f "usebackq" %%a in ('%FILE%') do set SIZE=%%~za

::: determine device serial number from drive volume
set LABEL=
for /f "tokens=1-5*" %%a in ('vol %DRIVE%') do (
    set LABEL=%%f & goto got_label
)
:got_label
SET SERIAL=00000
if "%LABEL:~0,6%"=="AX317_" set SERIAL=%LABEL:~6,5%
if "%LABEL:~0,4%"=="AX3_" set SERIAL=%LABEL:~4,7%
if "%LABEL:~0,6%"=="AX664_" set SERIAL=%LABEL:~6,5%
if "%LABEL:~0,4%"=="AX6_" set SERIAL=%LABEL:~4,7%

::: calculate the number of data blocks
set /a BLOCKS=%SIZE%-1024
set /a BLOCKS=%BLOCKS%/512
set /a DATA_BYTES=%BLOCKS%*480
set /a BLOCKS=%BLOCKS%+1

::: dump first and last sample blocks
if exist _temp.csv del _temp.csv
"%CWACONVERT%" "%FILE%" -nodata -battv -battp -blockstart 2 -blockcount 1 2> nul > _temp.csv
"%CWACONVERT%" "%FILE%" -nodata -battv -battp -blockstart %BLOCKS% -blockcount 1 2> nul >> _temp.csv

::: get start date/time/batt
set START_DATE=0000-01-01
set START_TIME=00:00:00
set START_BATTV=0
set START_BATTP=0
for /f "usebackq tokens=1,2,4,5,6 delims=,. " %%i in (`powershell -command "& {Get-Content _temp.csv -TotalCount 1}"`) do (
    set START_DATE=%%i
    set START_TIME=%%j
    set START_BATTV=%%k.%%l
    set START_BATTP=%%m
)

::: get end date/time/batt
set END_DATE=0000-01-01
set END_TIME=00:00:00
set END_BATTV=0
set END_BATTP=0
for /f "usebackq tokens=1,2,4,5,6 delims=,. " %%i in (`powershell -command "& {Get-Content _temp.csv | Select-Object -last 1}"`) do (
    set END_DATE=%%i
    set END_TIME=%%j
    set END_BATTV=%%k.%%l
    set END_BATTP=%%m
)

rem del _temp.csv

::: Extract start month, and day of month (remove leading zero)
set START_MONTH=%START_DATE:~5,2%
set START_DAY=%START_DATE:~8,2%
if %START_DAY:~0,1%==0 set START_DAY=%START_DAY:~1,1%


::: Extract end month, and day of month (remove leading zero)
set END_MONTH=%END_DATE:~5,2%
set END_DAY=%END_DATE:~8,2%
if %END_DAY:~0,1%==0 set END_DAY=%END_DAY:~1,1%


::: Start/end month in the same month, or can adjust if they are in different, but adjacent, months
if %START_MONTH%==%END_MONTH% goto months_match
if %START_MONTH%==01 SET /a END_DAY=END_DAY+31
if %START_MONTH%==02 SET /a END_DAY=END_DAY+28
if %START_MONTH%==03 SET /a END_DAY=END_DAY+31
if %START_MONTH%==04 SET /a END_DAY=END_DAY+30
if %START_MONTH%==05 SET /a END_DAY=END_DAY+31
if %START_MONTH%==06 SET /a END_DAY=END_DAY+30
if %START_MONTH%==07 SET /a END_DAY=END_DAY+31
if %START_MONTH%==08 SET /a END_DAY=END_DAY+31
if %START_MONTH%==09 SET /a END_DAY=END_DAY+30
if %START_MONTH%==10 SET /a END_DAY=END_DAY+31
if %START_MONTH%==11 SET /a END_DAY=END_DAY+30
if %START_MONTH%==12 SET /a END_DAY=END_DAY+31
:months_match


::: Calculate total duration (in hours)
SET END_DAY_HOUR=%END_TIME:~0,2%
if %END_DAY_HOUR:~0,1%==0 set END_DAY_HOUR=%END_DAY_HOUR:~1,1%
SET /a END_DAY_HOUR=END_DAY*24+END_DAY_HOUR
SET START_DAY_HOUR=%START_TIME:~0,2%
if %START_DAY_HOUR:~0,1%==0 set START_DAY_HOUR=%START_DAY_HOUR:~1,1%
SET /a START_DAY_HOUR=START_DAY*24+START_DAY_HOUR
set /a HOURS=END_DAY_HOUR-START_DAY_HOUR


::: Calculate battery change and average data rate
set /a BATTP=START_BATTP-END_BATTP
set RATE_BPS=0
if not %HOURS%==0 set /a RATE_BPS=DATA_BYTES/(HOURS*60*60)

::: Formatting
if %START_BATTP:~2,1%!==! set START_BATTP= %START_BATTP%
if %RATE_BPS:~2,1%!==! set RATE_BPS= %RATE_BPS%

rem echo drive=%DRIVE% serial=%SERIAL% label=%LABEL% file=%FILE% size=%SIZE% blocks=%BLOCKS% sample_bytes=%DATA_BYTES% days=%DAYS% batt=%BATTP%
echo %DRIVE% %SERIAL% %START_DATE:~8,2%/%START_DATE:~5,2%/%START_DATE:~2,2% %START_TIME:~0,8% - %END_DATE:~8,2%/%END_DATE:~5,2%/%END_DATE:~2,2% %END_TIME:~0,8%, %HOURS%h @~%RATE_BPS% Bps B%%(%START_BATTP%%%-%END_BATTP%%%)=%BATTP%%%  Bv(%START_BATTV%-%END_BATTV%)

if not exist quick-qc-check-log.csv echo Serial,Start,End,Hours,Data,Rate(Bps),BattStart(%%),BattEnd(%%),BattChange(%%),BattStart(V),BattEnd(V) >> quick-qc-check-log.csv

echo %SERIAL%,%START_DATE% %START_TIME%,%END_DATE% %END_TIME%,%HOURS%,%DATA_BYTES%,%RATE_BPS%,%START_BATTP%,%END_BATTP%,%BATTP%,%START_BATTV%,%END_BATTV% >> quick-qc-check-log.csv

goto :eof

@echo off
setlocal
echo CWA-to-Counts
echo ~~~~~~~~~~~~~
echo.

::: Set epoch size, e.g. to 1, 10, or 60 (seconds)
set EPOCH=60

::: Set to 1 to output raw files at 30Hz (in a format that can be converted from raw to epoch with ActiLife software)
set USE_RAW=

::: accel=accelerometer; ag=format matches that of "ActiGraph(tm) ActiLife" software; agdt=format matches that of "ActiGraph(tm) ActiLife" Data Table format (counts only)
::: (ag/agdt: Axis1=Y;Axis2=X;Axis3=Z)
::: ag:   Axis1,Axis2,Axis3
::: agdt: Date,Time,Axis1,Axis2,Axis3,Vector Magnitude
set CSV_FORMAT=agdt

:check_req
set OMCONVERT=%~dp0omconvert.exe
if exist "%OMCONVERT%" goto start
set Program32=%ProgramFiles%
if not "%ProgramFiles(x86)%"=="" set Program32=%ProgramFiles(x86)%
set OMCONVERT=%Program32%\Open Movement\OM GUI\Plugins\OmConvertPlugin\omconvert.exe
if exist "%OMCONVERT%" goto start
echo ERROR: omconvert.exe not found -- use a local copy or check 'OMGUI' installed in the default location? Expected at: %OMCONVERT%
pause
goto eof

:start
set FILECOUNT=0

:next
set FILE=%~1
if "%FILE%%FILECOUNT%"=="0" call :choosefile
if "%FILE%%FILECOUNT%"=="0" goto eof
if "%FILE%"=="" goto end
set /A FILECOUNT=FILECOUNT+1
call :process "%FILE%
shift
goto next

:process
set FILE=%~1
echo.
echo ----------------------------------------------------------------------
echo  Processing file: "%FILE%"
echo ----------------------------------------------------------------------

if /i "%FILE:~2,-1%"==":\CWA-DATA.CWA" goto file_device
if /i not "%~x1"==".CWA" goto file_type_error
if not exist "%~1" goto file_not_exist
set RAW_OPTION=
if %USE_RAW%!==1! set RAW_OPTION=-csv-file "%~dpn1.raw30ag.csv"
@echo on
"%OMCONVERT%" "%~1" -interpolate-mode 1 -resample 30 -csv-format:%CSV_FORMAT% %RAW_OPTION% -counts-epoch %EPOCH% -counts-file "%~dpn1.counts%EPOCH%.csv"
@if errorlevel 1 goto error_processing
@echo off
echo ======================================================================
goto :eof

:file_device
echo ERROR: Not designed to work on files straight from the device (the output goes to the current file's directory).
pause
goto :eof

:file_type_error
echo ERROR: Unknown file type ("%~x1"): %~1
pause
goto :eof

:file_not_exist
echo ERROR: File does not exist: %~1
pause
goto :eof

:error_processing
echo WARNING: There was a problem while processing file (%ERRORLEVEL%): %~1
echo Check the version of 'omconvert' is new enough: https://github.com/digitalinteraction/openmovement/blob/master/Downloads/AX3/AX3-GUI-revisions.md
pause
goto :eof

:choosefile
echo NOTE: Choose a .CWA file to process (you can also drag-and-drop one or more .CWA files on to this batch file).
set DIALOG="about:<input type=file id=file><script>file.click();new ActiveXObject('Scripting.FileSystemObject').GetStandardStream(1).WriteLine(file.value);close();resizeTo(0,0);</script>"
for /f "tokens=* delims=" %%f in ('mshta.exe %DIALOG%') do set "FILE=%%f"
goto :eof

:end

echo.
echo ----------------------------------------------------------------------
echo  Done
echo ======================================================================
pause
:eof

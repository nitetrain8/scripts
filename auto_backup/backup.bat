@echo off

:: Prompt for S/N & extract date code from windows `date` command
set /p SN="Enter bioreactor S/N (or exit to exit): "
if %SN% == exit goto :EOF
for /f "tokens=1,2" %%i in ('date /T') do set date=%%j
for /f "tokens=1,2,3 delims=/ " %%a in ("%date%") do set m=%%a&set d=%%b&set y=%%c
set y=%y:~2,3%


:: File Paths & Variables
set DCODE=%y%%m%%d%
set PTH=..\Customer_Backups\%SN% %DCODE%
set DBDIR="C:\database\*.*"
set LVDIR="C:\PBS\LabVIEW Data\*.*"
set FTPSCRIPT=backup_rio.bat
set DBBKUP=%PTH%\Database\
set LVBKUP=%PTH%\LabVIEW_Data\
set XOPS=/E /Y
set RIOBKUP=%PTH%\Rio_Config\

:: Make director(ies)
@echo on
mkdir "%DBBKUP%"
mkdir "%LVBKUP%"
mkdir "%RIOBKUP%"

:: Backups
@echo off
echo ===========================
echo Creating backups
echo ===========================
@echo on
xcopy %DBDIR% "%DBBKUP%" %XOPS%
xcopy %LVDIR% "%LVBKUP%" %XOPS%
call %FTPSCRIPT% "%RIOBKUP%"

:: Rename DB...
if exist "%DBBKUP%TestStand Results2.mdb" rename "%DBBKUP%TestStand Results2.mdb" "TestStand Results2 %DCODE%.mdb"
if exist "%DBBKUP%PBSBioreactorDatabase.mdb" rename "%DBBKUP%PBSBioreactorDatabase.mdb" "PBSBioreactorDatabase %DCODE%.mdb"

@echo off
echo ===========================
echo Finding Timezone
echo ===========================
call tz.bat

@echo.Backup Finished!
pause
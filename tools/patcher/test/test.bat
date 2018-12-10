@echo off

for /f %%i in ('cd') do set HERE=%%i

:: directories
set CLV=D:\Customer_Backups\000317J1801_backup 180221\LabVIEW_Data
set CRIO=D:\Customer_Backups\000317J1801_backup 180221\Rio_config

set REVB=D:\auto_hd_install\default configs\IM00226 Rev B
set REVC=D:\auto_hd_install\default configs\IM00226 Rev C

set ODIR=%REVB%\Mag 15
set NDIR=%REVC%\Mag 15

:: customer config paths
set CSYSV=%CRIO%\System Variables.sys
set CALM=%CRIO%\Alarms.alm
set CALMON=%CLV%\Alarms On.alm
set CALMOFF=%CLV%\Alarms Off.alm
set CLOGON=%CLV%\Logging On.log
set CLOGOFF=%CLV%\Logging Off.log
set CEMAIL=%CLV%\Email Alerts Settings.xml
set CRECIPE=%CLV%\Bioreactor Recipes.cfg

:: old config files
set OSYSV=%ODIR%\System Variables.sys
set OALM=%ODIR%\Alarms.alm
set OALMON=%ODIR%\Alarms On.alm
set OALMOFF=%ODIR%\Alarms Off.alm
set OLOGON=%ODIR%\Logging On.log
set OLOGOFF=%ODIR%\Logging Off.log
set OEMAIL=%ODIR%\Email Alerts Settings.xml
set ORECIPE=%ODIR%\Bioreactor Recipes.cfg

:: new config files
set NSYSV=%NDIR%\System Variables.sys
set NALM=%NDIR%\Alarms.alm
set NALMON=%NDIR%\Alarms On.alm
set NALMOFF=%NDIR%\Alarms Off.alm
set NLOGON=%NDIR%\Logging On.log
set NLOGOFF=%NDIR%\Logging Off.log
set NEMAIL=%NDIR%\Email Alerts Settings.xml
set NRECIPE=%NDIR%\Bioreactor Recipes.cfg

:: patch files
set NULLPATCH=test.empty.patch

set PYCMD=python ..\src\merge\merge.py

@echo on
:: sysv
::%PYCMD% "%NULLPATCH%" "%CSYSV%" "%OSYSV%" "%NSYSV%" --type=sysvars

%PYCMD% -h

:: alarms
::%PYCMD% "%NULLPATCH%" "%CALM%" "%OALM%" "%NALM%" --type=alarms
::%PYCMD% "%NULLPATCH%" "%CALMON%" "%OALMON%" "%NALMON%" --type=alarms
::%PYCMD% "%NULLPATCH%" "%CALMOFF%" "%OALMOFF%" "%NALMOFF%" --type=alarms

:: logger settings
::%PYCMD% "%NULLPATCH%" "%CLOGON%" "%OLOGON%" "%NLOGON%" --type=loggersettings
::%PYCMD% "%NULLPATCH%" "%CLOGOFF%" "%OLOGOFF%" "%NLOGOFF%" --type=loggersettings

:: email
::%PYCMD% "%NULLPATCH%" "%CEMAIL%" "%OEMAIL%" "%NEMAIL%" --type=emailsettings

::@%PYCMD% "%NULLPATCH%" "%CRECIPE%" "%ORECIPE%" "%NRECIPE%" --type=recipes --loggersettings="%NLOGOFF%"
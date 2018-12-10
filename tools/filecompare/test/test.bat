@echo off
set RUNFC=python ..\src\filecompare\filecompare.py
:: set RUNFC=..\builds\filecompare.exe
rem set TYPES[1]=sysvars
rem set TYPES[2]=alarms
rem set TYPES[3]=calfactors
rem set TYPES[4]=reportsettings
rem set TYPES[5]=emailsettings
rem set TYPES[6]=loggersettings

rem set EXT[1]=sys
rem set EXT[2]=alm
rem set EXT[3]=cfg
rem set EXT[4]=cfg
rem set EXT[5]=xml
rem set EXT[6]=log

rem setlocal EnableDelayedExpansion
rem for /L %%i IN (1,1,6) DO (
rem     set EX=!EXT[%%i]!
rem     set REF=files\!TYPES[%%i]!\ref.!EX!
rem     set F1=files\!TYPES[%%i]!\file1.!EX!
rem     set F2=files\!TYPES[%%i]!\file2.!EX!
rem     set F3=files\!TYPES[%%i]!\file3.!EX!
rem     set vector[%%i]=%RUNFC% !TYPES[%%i]! !REF! !F1! !F2! !F3! %1
rem )

rem @echo off
rem echo.>>bob.txt
rem for /L %%i in (1,1,6) DO (
rem     echo !vector[%%i]!>> bob.txt
rem     !vector[%%i]!
rem )
rem endlocal
set OUTFMT=csv

%RUNFC% sysvars files\sysvars\ref.sys files\sysvars\file1.sys files\sysvars\file2.sys files\sysvars\file3.sys %* --logfile=files\sysvars.%OUTFMT% --outfmt=%OUTFMT%
%RUNFC% alarms files\alarms\ref.alm files\alarms\file1.alm files\alarms\file2.alm files\alarms\file3.alm %* --logfile=files\alarms.%OUTFMT% --outfmt=%OUTFMT%
%RUNFC% calfactors files\calfactors\ref.cfg files\calfactors\file1.cfg files\calfactors\file2.cfg files\calfactors\file3.cfg %* --logfile=files\calfactors.%OUTFMT% --outfmt=%OUTFMT%
%RUNFC% reportsettings files\reportsettings\ref.cfg files\reportsettings\file1.cfg files\reportsettings\file2.cfg files\reportsettings\file3.cfg %* --logfile=files\reportsettings.%OUTFMT% --outfmt=%OUTFMT%
%RUNFC% emailsettings files\emailsettings\ref.xml files\emailsettings\file1.xml files\emailsettings\file2.xml files\emailsettings\file3.xml %* --logfile=files\emailsettings.%OUTFMT% --outfmt=%OUTFMT%
%RUNFC% loggersettings files\loggersettings\ref.log files\loggersettings\file1.log files\loggersettings\file2.log files\loggersettings\file3.log %* --logfile=files\loggersettings.%OUTFMT% --outfmt=%OUTFMT%

echo "testing batch mode"
::pause 

%RUNFC% batchmode test.txt
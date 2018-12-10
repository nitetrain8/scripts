@echo off

:: Config files
set LVDATA="C:\PBS\LabVIEW Data\"
set ATOM=".\config\atom\*.*"
set RIO=".\config\rio\*.*"
set COMMON=".\config\common\*.*"
set UNZIP=".\vbs\unzip.vbs"
set ZIP=".\vbs\zip.vbs"

:: RIO Images and folder targets
set RIO_IMAGES=.\RIO Images
set RIO_TARGET=C:\PBS\builds\RIO_Images
set Z9641="%RIO_IMAGES%\80L-9641.zip"
set Z9642="%RIO_IMAGES%\80L-9642.zip"
set F9641="%RIO_IMAGES%\80L-9641\"
set F9642="%RIO_IMAGES%\80L-9642\"
set RIO_CONF41="%RIO_IMAGES%\80L-9641\Config"
set RIO_CONF42="%RIO_IMAGES%\80L-9642\Config"
set ZO41="%RIO_IMAGES%\80L-9641-out.zip"
set ZO42="%RIO_IMAGES%\80L-9642-out.zip"

:: RIO Image file output
set Z41_TARGET="%RIO_TARGET%\80L-9641.zip"
set Z42_TARGET="%RIO_TARGET%\80L-9642.zip"


@echo on

:: Copy config files to LabVIEW Data Folder
xcopy %ATOM% %LVDATA% /E /Y
xcopy %COMMON% %LVDATA% /E /Y

:: Unzip RIO Images
call %UNZIP% %Z9641% %F9641%
call %UNZIP% %Z9642% %F9642%

:: Copy config files to RIO Image config folder
xcopy %RIO% %RIO_CONF41% /E /Y
xcopy %COMMON% %RIO_CONF41% /E /Y
xcopy %RIO% %RIO_CONF42% /E /Y
xcopy %COMMON% %RIO_CONF42% /E /Y

:: Re-zip to unique output filename
:: This ensures no irreversible changes 
:: are made, in case of error or necessary
:: user interaction / modification of process
call %ZIP% %F9641% %ZO41%
call %ZIP% %F9642% %ZO42%

:: Copy zip files to target
copy %ZO41% %Z41_TARGET% /Y
copy %ZO42% %Z42_TARGET% /Y

call "C:\Program Files\PBS 80L Rio Installer\80L Install RIO.exe"
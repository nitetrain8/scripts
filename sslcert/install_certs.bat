@echo off
set /p CONTINUE=CONFIRM SYSTEM IS OFFLINE BEFORE CONTINUING (y/n):
if "%CONTINUE%" neq "y" (
 goto :stop
)
sadmin bu
call gen_key.bat
sadmin eu
echo Script Finished!
timeout /t -1

goto :end

:stop:
echo exiting
:end:
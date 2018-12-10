@echo off
:: String parsing in batch is the WORST
:: tzutil is also the WORST
:: This script stucked to write, but it seems to work (??)

setlocal enabledelayedexpansion
set TGT=
for /f "delims=" %%i in ('tzutil /g') do (
    :: strip whitespace
    set input=%%i
    for /l %%a in (1,1,100) do if "!input:~-1!"==" " set input=!input:~0,-1!
    set TGT=!input!
)

:: I'm not exactly sure why
:: you need to do this but I
:: think the previous local
:: scope messes with the second
:: loop?

(ENDLOCAL & REM.-- RETURN VALUES
  SET TGT2=%TGT%%~2
)
setlocal enabledelayedexpansion
for /f "tokens=*" %%a in ('tzutil /l') do (
    :: Strip whitespace
    set input=%%a
    for /l %%a in (1,1,100) do if "!input:~-1!"==" " set input=!input:~0,-1!
    if "!input!"=="%TGT2%" (set FND=!PREV!)
    set PREV=!input!
)
echo "%FND%"
@echo off

"C:\Program Files\WinSCP\WinSCP.com" ^
  /ini=nul ^
  /command ^
    "open ftp://anonymous:anonymous%%40example.com@100.100.100.145/" ^
    "cd /" ^
    "lcd "%1"" ^
    "get /config/*" ^
    "exit"

set WINSCP_RESULT=%ERRORLEVEL%
if %WINSCP_RESULT% equ 0 (
  echo Success
) else (
  echo Error
)

exit /b %WINSCP_RESULT%

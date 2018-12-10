@echo off
set HERE=%~dp0
cd ..
set TGT=D:\patcher
del /s /f /q %TGT%\*.*
for /f %%f in ('dir /ad /b %TGT%\') do rd /s /q %TGT%\%%f
cmd /c xcopy patcher D:\patcher /y /E
cd %HERE%
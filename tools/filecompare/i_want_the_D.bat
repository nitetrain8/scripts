@echo off
set HERE=%~dp0
cd ..
set THIS=filecompare
set TGT=D:\%THIS%
del /s /f /q %TGT%\*.*
for /f %%f in ('dir /ad /b %TGT%\') do rd /s /q %TGT%\%%f
cmd /c xcopy %THIS% %TGT%\ /y /E
cd %HERE%
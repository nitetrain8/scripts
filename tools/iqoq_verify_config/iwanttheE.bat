@echo off

set curdir=%CD%
set HERE=%~dp0
cd %HERE%\..\
set THIS=iqoq_verify_config
set TGT=E:\IQOQ_3L_Mag\verify_files
del /s /f /q %TGT%\*.*
for /f %%f in ('dir /ad /b %TGT%\') do rd /s /q %TGT%\%%f
cmd /c xcopy %THIS% %TGT%\ /y /E
cd %curdir%
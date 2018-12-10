@echo off
set HERE=%~dp0
cd ..
set THIS=iqoq_verify_config
set TGT=D:\IQOQ_3L_Mag\verify_files
del /s /f /q %TGT%\*.*
for /f %%f in ('dir /ad /b %TGT%\') do rd /s /q %TGT%\%%f
cmd /c xcopy %THIS% %TGT%\ /y /E
cd %HERE%
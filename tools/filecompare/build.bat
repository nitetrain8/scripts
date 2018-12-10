@echo off
:: Save the current working directory and cd to the build
:: directory. This simplifies a LOT of scripting throughout
:: the build processs.
for /f %%i in ('cd') do set HERE=%%i
cd %~dp0

:: Ensure PyInstaller 32 bit is set to the correct path!!!
:: Note - if PyInstaller executable is in PATH, this only needs
:: to refer to the correct executable name
set PYI32=pyinstaller

:: Path to the .spec file that contains the build instructions
:: for pyinstaller. To rebuild this file, run "pyinstaller merge.py".
:: Note that this will overwrite any custom changes to the .spec file
:: with no warning!
set SPEC=merge.spec

:: Most options are set in custom scripts or in the spec file itself
:: Set any others here. 
:: Reference: https://pythonhosted.org/PyInstaller/usage.html
:: Notes:
:: --onefile: makes the distributable a single EXE. The EXE unzips 
::            itself to a temporary directory when it runs, then
::            deletes it on exit. 
:: --distpath: By default, the binary ends up in ./dist and the
::             intermediate files end up in ./build. I changed
::             this to keep terminology similar between LabVIEW
::             and this script for convenience. 
:: --workpath: See above. 
:: --noconfirm: No warning when overwriting output files
set OPTIONS=--onefile --distpath .\builds --workpath .\intermediates --clean --noconfirm


copy %SPEC% %SPEC%.backup

:: Execute!
echo %PYI32% %SPEC% %OPTIONS%
%PYI32% %SPEC% %OPTIONS%

:: CD back to caller's WD
cd %HERE%
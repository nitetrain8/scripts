@echo off

for /f %%i in ('cd') do set HERE=%%i
cd %~dp0\test_scripts\


:: Don't run create_merge_imports if running in EXE mode - 
:: this will be created automatically by the build test_script
:: if it needs to run. 

:: The build script checks the st_mtime_ns of the merge_handlers
:: and EXE files to determine whether to run the (lengthy) rebuild.
:: If create_merge_imports is run here, then it would always
:: rebuild. 

if [%1] equ [--exe] (
    echo Running in EXE mode!
) else (
    python ..\..\..\create_merge_imports.py
)

:: The lv_parse file is required for verifying
:: that system variables files are parsed correctly.

:: Verifying that this file itself functions correctly
:: should be done as a separate set of unittests, which
:: should cause the test suite to abort if errors are
:: found. 

python -m pytest -v -s %1
cd %HERE%
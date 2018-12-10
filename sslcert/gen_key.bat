:: Edit config info here!
@echo off
set C=US
set ST=California
set L=Camarillo
set O=PBS Biotech
set emailAddress=pbs@pbsbiotech.com
set ALGO=rsa:4096
set DAYS=999999
set OUTDIR=out
set KEYFILE=server_101.key
set CERTFILE=server_101.cer
set KEYOUT=%OUTDIR%\%KEYFILE%
set CERTOUT=%OUTDIR%\%CERTFILE%
set CERTLOC=localMachine
set NIFOLDER=C:/programdata/national instruments/certstore/server_certs
set NICERTDST="%NIFOLDER%\%CERTFILE%"
set NIKEYDST="%NIFOLDER%\%KEYFILE%"

:: Don't touch!
set CN=localhost
set OPENSSL=openssl.exe
set OPENSSLCONF=openssl.cfg
set ARGS=/emailAddress=%emailAddress%/C=%C%/ST=%ST%/L=%L%/O=%O%/CN=%CN%
set SUB=-subj "%ARGS%"
set CERTMGR=certmgr.exe
set OPENSSL_CONF=openssl.cfg 
set SSLCMD=req -config %OPENSSLCONF% -nodes -extensions SAN -newkey %ALGO% -keyout %KEYOUT% %SUB% -x509 -days %DAYS% -out %CERTOUT%
set CERTMGRCMD=%CERTMGR% /add -c %NICERTDST% /s /r %CERTLOC% root

:: Make out folder
IF EXIST out (
    rmdir /S /Q out
)
mkdir out

:: Generate private and public key. No CSR generated.
echo %OPENSSL% %SSLCMD%
%OPENSSL% %SSLCMD%
rem CALL :check_err

rem :: Copy to NI folder
rem echo copying %KEYFILE% to NI folder...
rem copy %KEYOUT% %NIKEYDST%
rem echo copying %CERTFILE% to NI folder...
rem copy %CERTOUT% %NICERTDST%

rem :: Install certificate

rem echo %CERTMGRCMD%
rem %CERTMGRCMD%
rem CALL :check_err

rem rmdir /S /Q %OUTDIR%
rem @echo off

rem goto :end

rem :check_err:
rem IF "%ERRORLEVEL%" NEQ "0" (
rem     echo "Error: exiting"
rem     goto :end
rem )
rem :end:
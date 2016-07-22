@echo off
pushd %~dp0
    :: Running prompt elevated
:-------------------------------------
REM  --> Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"
:--------------------------------------

IF EXIST C:\Python27 (
set PATH2=C:\Python27
) ELSE (
echo Python path not found, please specify or install.
set /p PATH2= Specify Python path: 
)

setx PATH "%PATH%;%PATH2%;%PATH2%\Scripts;"

popd

%PATH2%\python get-pip.py
cd ..
%PATH2%\Scripts\pip install -r requirements.txt
%PATH2%\Scripts\pip install -r requirements.txt --upgrade
cd config
set /p API= Enter your Google API key here:

    (
    echo {
    echo "gmaps_key" : "%API%"
    echo }
    ) > credentials.json
echo All done!
pause

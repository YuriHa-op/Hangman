@echo off
REM Hangman Python Client Setup Script

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo IMPORTANT: You must install omniORB and omniORBpy manually!
echo Download from: https://sourceforge.net/projects/omniorb/files/
echo.
echo After installing omniORB/omniORBpy, generate Python stubs with:
echo   omniidl -bpython ..\CORBA_IDLs\GameService.idl
echo and copy the generated files to ..\Client_Python\
echo.
pause 
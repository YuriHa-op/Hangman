@echo off
:: Set the JAVA_HOME and PATH variables
set JAVA_HOME=C:\Program Files\Java\corretto-1.8.0_442
set PATH=%JAVA_HOME%\bin;%PATH%

:: Run the CORBA client
cd src
java client.ClientMain -ORBInitialPort 1050 -ORBInitialHost localhost

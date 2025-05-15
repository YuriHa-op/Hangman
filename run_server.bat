@echo off
:: Set the JAVA_HOME and PATH variables
set JAVA_HOME=C:\Program Files\Java\corretto-1.8.0_442
set PATH=%JAVA_HOME%\bin;%PATH%

:: Start the CORBA Naming Service (make sure to run this first)
start /B tnameserv -ORBInitialPort 900
:: Run the CORBA server
cd src
java server.ServerMain -ORBInitialPort 900 -ORBInitialHost localhost

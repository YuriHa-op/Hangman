@echo off
echo Compiling GameService.idl...
idlj -fall -td src/main/java src/main/java/idl/GameService.idl

echo Compiling LoginService.idl...
idlj -fall -td src/main/java src/main/java/idl/LoginService.idl

echo Compiling AdminService.idl...
idlj -fall -td src/main/java src/main/java/idl/AdminService.idl

echo IDL compilation complete! 
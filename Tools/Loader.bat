@echo off
title Injectiine
:Menu
cls
echo :::::::::::::::::::::::::
echo ::Welcome to Injectiine::
echo :::::::::::::::::::::::::
echo.
echo Please select a console.
echo NES  (1)
echo SNES (2)
echo N64  (3)
echo GBA  (4)
echo NDS  (5)
echo.
set /p CHOICE=[Your Choice:] 
if %CHOICE%==1 GOTO:NES
if %CHOICE%==2 GOTO:SNES
if %CHOICE%==3 GOTO:N64
if %CHOICE%==4 GOTO:GBA
if %CHOICE%==5 GOTO:NDS
GOTO:Menu

:NES
cd CONSOLES
cd NES
call NES.bat
exit

:SNES
cd CONSOLES
cd SNES
call SNES.bat
exit

:N64
cd CONSOLES
cd N64
call N64.bat
exit

:GBA
cd CONSOLES
cd GBA
call GBA.bat
exit

:NDS
cd CONSOLES
cd NDS
call NDS.bat
exit

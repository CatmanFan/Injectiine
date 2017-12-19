@echo off
title Injectiine [NDS]
cls
cd ..
cd ..
cd ..
cd Files

echo ::::::::::::::::::::
echo ::INJECTIINE [NDS]::
echo ::::::::::::::::::::
SLEEP 3

:: CHECK THAT FILES EXIST

IF NOT EXIST *.nds GOTO:LastChance
IF NOT EXIST bootTvTex.png GOTO:404ImagesNotFound
IF NOT EXIST iconTex.png GOTO:404ImagesNotFound

cd ..
cd Tools
cd CONSOLES
cd NDS

:BASE
cls
echo Which base do you want to use?
echo Brain Age [USA]             (1)
echo Brain Training [EUR]        (2)
echo Kirby Squeak Squad [USA]    (3)
echo Kirby Mouse Attack [EUR]    (4)
echo New Super Mario Bros. [USA] (5)
echo New Super Mario Bros. [EUR] (6)
echo Base supplied from Files    (7)
echo.
set /p BASEDECIDE=[Your Choice:] 
IF %BASEDECIDE%==1 GOTO:BA
IF %BASEDECIDE%==2 GOTO:BT
IF %BASEDECIDE%==3 GOTO:KSS
IF %BASEDECIDE%==4 GOTO:KMA
IF %BASEDECIDE%==5 GOTO:NSMBU
IF %BASEDECIDE%==6 GOTO:NSMBE
IF %BASEDECIDE%==7 GOTO:BaseNotice
GOTO:BASE

:BaseNotice
cls
echo Please supply your base, including the code, content and meta
echo folders, in a directory called "Base" within the Files directory.
echo.
echo Press any key to continue.
pause>NUL
cd ..
cd ..
cd ..
cd Files
IF NOT EXIST Base GOTO:BASEFAIL
cd ..
cd Tools
cd CONSOLES
cd NDS
GOTO:EnterCommon

:: ENTERING KEYS

:WrongKeyBA
cls
echo Title key is incorrect. Please try again.
SLEEP 2

:EnterKeyBA
cls

IF EXIST TitleKeyBA.txt goto:EnterCommon
echo This step will not be required the next time you start Injectiine.
echo Enter the title key for Brain Age (USA):
set /p TITLEKEY=
echo %TITLEKEY:~0,32%>TitleKeyBA.txt
set /p TITLEKEY=<TitleKeyBA.txt
cls
IF "%TITLEKEY:~0,4%"=="cdee" GOTO:EnterCommon ELSE GOTO:WrongKeyBA

:WrongKeyBT
cls
echo Title key is incorrect. Please try again.
SLEEP 2

:EnterKeyBT
cls

IF EXIST TitleKeyBT.txt goto:EnterCommon
echo This step will not be required the next time you start Injectiine.
echo Enter the title key for Brain Training (EUR):
set /p TITLEKEY=
echo %TITLEKEY:~0,32%>TitleKeyBT.txt
set /p TITLEKEY=<TitleKeyBT.txt
cls
IF "%TITLEKEY:~0,4%"=="34a3" GOTO:EnterCommon ELSE GOTO:WrongKeyBT

:: KIRBY

:WrongKeyKSS
cls
echo Title key is incorrect. Please try again.
SLEEP 2

:EnterKeyKSS
cls

IF EXIST TitleKeyKSS.txt goto:EnterCommon
echo This step will not be required the next time you start Injectiine.
echo Enter the title key for Kirby Squeak Squad (USA):
set /p TITLEKEY=
echo %TITLEKEY:~0,32%>TitleKeyKSS.txt
set /p TITLEKEY=<TitleKeyKSS.txt
cls
IF "%TITLEKEY:~0,4%"=="fdfe" GOTO:EnterCommon ELSE GOTO:WrongKeyKSS

:WrongKeyKMA
cls
echo Title key is incorrect. Please try again.
SLEEP 2

:EnterKeyKMA
cls

IF EXIST TitleKeyKMA.txt goto:EnterCommon
echo This step will not be required the next time you start Injectiine.
echo Enter the title key for Kirby Mouse Attack (EUR):
set /p TITLEKEY=
echo %TITLEKEY:~0,32%>TitleKeyKMA.txt
set /p TITLEKEY=<TitleKeyKMA.txt
cls
IF "%TITLEKEY:~0,4%"=="9d52" GOTO:EnterCommon ELSE GOTO:WrongKeyKMA

:: NSMB

:WrongKeyNSMBU
cls
echo Title key is incorrect. Please try again.
SLEEP 2

:EnterKeyNSMBU
cls

IF EXIST TitleKeyNSMBU.txt goto:EnterCommon
echo This step will not be required the next time you start Injectiine.
echo Enter the title key for New Super Mario Bros. (USA):
set /p TITLEKEY=
echo %TITLEKEY:~0,32%>TitleKeyNSMBU.txt
set /p TITLEKEY=<TitleKeyNSMBU.txt
cls
IF "%TITLEKEY:~0,4%"=="9fe3" GOTO:EnterCommon ELSE GOTO:WrongKeyNSMBU

:WrongKeyNSMBE
cls
echo Title key is incorrect. Please try again.
SLEEP 2

:EnterKeyNSMBE
cls

IF EXIST TitleKeyNSMBE.txt goto:EnterCommon
echo This step will not be required the next time you start Injectiine.
echo Enter the title key for New Super Mario Bros. (EUR):
set /p TITLEKEY=
echo %TITLEKEY:~0,32%>TitleKeyNSMBE.txt
set /p TITLEKEY=<TitleKeyNSMBE.txt
cls
IF "%TITLEKEY:~0,4%"=="54b4" GOTO:EnterCommon ELSE GOTO:WrongKeyNSMBE

:: BASES

:BA
set BASEID=0005000010179b00
set BASEPDC=DAAE
set BASEFOLDER="Brain Age Train Your Brain In Minutes A Day [DAAE01]"
IF EXIST TitleKeyBA.txt (set /p TITLEKEY=<TitleKeyBA.txt) ELSE (GOTO :EnterKeyBA)
GOTO:EnterCommon

:BT
set BASEID=0005000010179c00
set BASEPDC=DAAP
set BASEFOLDER="Dr Kawashima's Brain Training How Old Is Your Brain [DAAP01]"
IF EXIST TitleKeyBT.txt (set /p TITLEKEY=<TitleKeyBT.txt) ELSE (GOTO :EnterKeyBT)
GOTO:EnterCommon

:KSS
set BASEID=00050000101a5600
set BASEPDC=DAKE
set BASEFOLDER="Kirby Squeak Squad [DAKE01]"
IF EXIST TitleKeyKSS.txt (set /p TITLEKEY=<TitleKeyKSS.txt) ELSE (GOTO :EnterKeyKSS)
GOTO:EnterCommon

:KMA
set BASEID=00050000101a5700
set BASEPDC=DAKP
set BASEFOLDER="Kirby Mouse Attack [DAKP01]"
IF EXIST TitleKeyKMA.txt (set /p TITLEKEY=<TitleKeyKMA.txt) ELSE (GOTO :EnterKeyKMA)
GOTO:EnterCommon

:NSMBU
set BASEID=0005000010195a00
set BASEPDC=DADE
set BASEFOLDER="New Super Mario Bros. [DADE01]"
IF EXIST TitleKeyNSMBU.txt (set /p TITLEKEY=<TitleKeyNSMBU.txt) ELSE (GOTO :EnterKeyNSMBU)
GOTO:EnterCommon

:NSMBE
set BASEID=0005000010195b00
set BASEPDC=DADP
set BASEFOLDER="NEW SUPER MARIO BROS. [DADP01]"
IF EXIST TitleKeyNSMBE.txt (set /p TITLEKEY=<TitleKeyNSMBE.txt) ELSE (GOTO :EnterKeyNSMBE)
GOTO:EnterCommon

:WrongCommon
cls
echo Wii U Common Key is incorrect. Please try again.
SLEEP 2

:EnterCommon
cls
IF EXIST NUSPacker/encryptKeyWith goto:EnterParameters
cd NUSPacker
echo This step will not be required the next time you start Injectiine.
set /p COMMON=Enter the Wii U Common Key: 
echo %COMMON:~0,32%>encryptKeyWith
set /p COMMON=<encryptKeyWith
cls
cd ..
echo http://ccs.cdn.wup.shop.nintendo.net/ccs/download>JNUSTool\config
echo %COMMON:~0,32%>>JNUSTool\config
echo https://tagaya.wup.shop.nintendo.net/tagaya/versionlist/EUR/EU/latest_version>>JNUSTool\config
echo https://tagaya-wup.cdn.nintendo.net/tagaya/versionlist/EUR/EU/list/%d.versionlist>>JNUSTool\config
IF "%COMMON:~0,4%"=="34a3" GOTO:EnterParameters ELSE GOTO:WrongCommon

:: ENTER PARAMETERS

:EnterParameters
cls

set TITLEID=%random:~-1%%random:~-1%%random:~-1%%random:~-1%

:LineQuestion
echo How many lines does your game name use?
set /p LINEDECIDE=[1/2:] 
echo.
IF %LINEDECIDE%==1 GOTO:LINE1
IF %LINEDECIDE%==2 GOTO:LINE2
GOTO:LINEQUESTION

:LINE1
echo Enter the name of the game.
set /p GAMENAME=[Game Name:] 
echo.
GOTO:RestOfParameters

:LINE2
echo Enter a short version of the name of the game.
set /p GAMENAME=[Short Game Name:] 
echo.

echo Enter the game name's first line.
set /p GAMENAME1=[Game Name Line 1:] 
echo.

echo Enter the game name's second line.
set /p GAMENAME2=[Game Name Line 2:] 
echo.

:RestOfParameters
echo Enter a 4-digit product code.
set /p PRODUCTCODE=[0-Z:] 
echo.

echo Do you want to enter a title ID manually?
echo If you don't, one will be randomly assigned.
set /p TITLEDECIDE=[Y/N:] 
echo.
IF /i "%TITLEDECIDE%"=="y" (
echo Enter a 4-digit meta title ID. Must only be hex values.
set /p TITLEID=[0-F:] 
)
cls

echo Injectiine will now create an NDS injection.
echo If you don't accept this, you will need to reenter your parameters.
CHOICE /C YN
IF errorlevel 2 goto :EnterParameters
IF errorlevel 1 goto :DownloadingStuff

:: DOWNLOADING AND MOVING STUFF

:DownloadingStuff
cls
IF %BASEDECIDE%==7 GOTO:EnterBaseCode
echo Testing Internet connection...
C:\windows\system32\PING.EXE google.com
if %errorlevel% GTR 0 goto:InternetSucks

IF EXIST WORKDIR echo Cleaning up working directory from last failed conversion...
IF EXIST WORKDIR rd /s /q WORKDIR
SLEEP 1
cd JNUSTool
echo Downloading base files...
rmdir /s /q %BASEFOLDER%
:COSXML
java -jar JNUSTool.jar %BASEID% %TITLEKEY% -file /code/cos.xml
IF NOT EXIST %BASEFOLDER%\code\cos.xml GOTO:COSXML
:RESTOFSTUFF
java -jar JNUSTool.jar %BASEID% %TITLEKEY% -file /code/hachihachi_ntr.rpx
java -jar JNUSTool.jar %BASEID% %TITLEKEY% -file /content/0010/.*
java -jar JNUSTool.jar %BASEID% %TITLEKEY% -file /meta/Manual.bfma
java -jar JNUSTool.jar %BASEID% %TITLEKEY% -file /meta/bootMovie.h264
java -jar JNUSTool.jar %BASEID% %TITLEKEY% -file /meta/bootLogoTex.tga
java -jar JNUSTool.jar %BASEID% %TITLEKEY% -file /meta/bootSound.btsnd

:MovingStuff
echo Moving to work directory...
C:\Windows\System32\Robocopy.exe %BASEFOLDER% ..\WORKDIR\ /MIR
rmdir /s /q %BASEFOLDER%
cd ..
IF NOT EXIST WORKDIR GOTO:ROBOFAIL
cd WORKDIR
cd content
cd ..
cd ..
cls
GOTO:InjectingROM

:EnterBaseCode
echo Enter the 4-digit product code of your base. You can also specify a custom one.
echo EXAMPLES: DOPE, DAAP, DAEJ
set /p BASEPDC=[Base Product Code:] 

:CopyBase
cls
echo Moving base to work directory...
C:\Windows\System32\Robocopy.exe ..\..\..\Files\Base WORKDIR\ /MIR
IF NOT EXIST WORKDIR GOTO:ROBOFAIL
rmdir /s /q ..\..\..\Files\Base
cls

:: INJECTING ROM
:InjectingROM
echo Injecting ROM...
cd ..
cd ..
cd ..
cd Files
IF EXIST iconTex.png (move iconTex.png ../Tools/png2tga)
IF NOT EXIST bootDrcTex.png (copy bootTvTex.png bootDrcTex.png)
IF EXIST bootTvTex.png (move bootTvTex.png ../Tools/png2tga)
IF EXIST bootDrcTex.png (move bootDrcTex.png ../Tools/png2tga)
IF EXIST bootLogoTex.png (move bootLogoTex.png ../Tools/png2tga)
IF EXIST drcback.png (move drcback.png ../Tools/CONSOLES/NDS/WORKDIR/content/0010/assets/textures/drcback.png)
IF EXIST tvback.png (move tvback.png ../Tools/CONSOLES/NDS/WORKDIR/content/0010/assets/textures/tvback.png)
IF EXIST nds1st_31p.png (move nds1st_31p.png ../Tools/CONSOLES/NDS/WORKDIR/content/0010/assets/textures/nds1st_31p.png)
IF EXIST nds1st_31p_tv.png (move nds1st_31p_tv.png ../Tools/CONSOLES/NDS/WORKDIR/content/0010/assets/textures/nds1st_31p_tv.png)

IF EXIST bootSound.wav echo bootSound detected. Do you want it to loop?
IF EXIST bootSound.wav set /p AUDIODECIDE=[Y/N:]
IF /i "%AUDIODECIDE%"=="n" set LOOP=-noLoop
IF EXIST bootSound.wav ..\Tools\sox\sox.exe .\bootSound.wav -b 16 bootEdited.wav channels 2 rate 48k trim 0 6
IF EXIST bootEdited.wav ..\Tools\wav2btsnd.jar -in bootEdited.wav -out bootSound.btsnd %LOOP%
IF EXIST bootSound.wav (2>NUL del bootSound.wav)
IF EXIST bootEdited.wav (2>NUL del bootEdited.wav)
IF EXIST bootSound.btsnd (move bootSound.btsnd ../Tools/CONSOLES/NES/WORKDIR/meta/bootSound.btsnd)

ren *.nds ROM.nds
2>NUL ren *.srl ROM.nds
cd ..
move Files\ROM.nds Tools\CONSOLES\NDS\7za\WUP-N-%BASEPDC%.srl
cd Tools
cd CONSOLES
cd NDS
cd WORKDIR
cd content
cd 0010
2>NUL del rom.zip
cd ..
cd ..
cd ..
cd 7za
7za a rom.zip "WUP-N-%BASEPDC%.srl"
del /s WUP-N-%BASEPDC%.srl >nul 2>&1
cd ..
copy fnr.exe WORKDIR\fnr.exe
move 7za\rom.zip WORKDIR\content\0010\rom.zip
cls

:: EDITING CONFIGURATION_CAFE.JSON AND APP.XML AND META.XML

cd WORKDIR

GOTO:Finishing

:ThreeDcafe
echo Do you want to upscale the VC emulator's 3D rendering?
echo May cause some graphical glitches.
echo.
echo If the game you're injecting doesn't use 3D, please select N.
echo.
set /p RENDERDECIDE=[Y/N:] 
echo.
IF /i "%RENDERDECIDE%"=="y" (
set RENDERSCALE=2
fnr --cl --dir "%cd%\content" --fileMask "configuration_cafe.json" --useRegEx --find "("RenderScale": )(.{1})" --replace "$1%RENDERSCALE%"
GOTO:Finishing
)
IF /i "%RENDERDECIDE%"=="n" (
GOTO:Finishing
)
GOTO:ThreeDcafe

:Finishing
echo Generating app.xml...
cd code
del /s app.xml >nul 2>&1
echo ^<?xml version="1.0" encoding="utf-8"?^>>app.xml
echo ^<app type="complex" access="777"^>>>app.xml
echo   ^<version type="unsignedInt" length="4"^>15^</version^>>>app.xml
echo   ^<os_version type="hexBinary" length="8"^>000500101000400A^</os_version^>>>app.xml
echo   ^<title_id type="hexBinary" length="8"^>000500001337%TITLEID%^</title_id^>>>app.xml
echo   ^<title_version type="hexBinary" length="2"^>0000^</title_version^>>>app.xml
echo   ^<sdk_version type="unsignedInt" length="4"^>21107^</sdk_version^>>>app.xml
echo   ^<app_type type="hexBinary" length="4"^>80000000^</app_type^>>>app.xml
echo   ^<group_id type="hexBinary" length="4"^>00001337^</group_id^>>>app.xml
echo   ^<os_mask type="hexBinary" length="32"^>0000000000000000000000000000000000000000000000000000000000000000^</os_mask^>>>app.xml
echo ^</app^>>>app.xml
SLEEP 1
cls

echo Generating meta.xml...
cd ..
cd meta
echo ^<?xml version="1.0" encoding="utf-8"?^>>meta.xml
echo ^<menu type="complex" access="777"^>>>meta.xml
echo   ^<version type="unsignedInt" length="4"^>33^</version^>>>meta.xml
echo   ^<product_code type="string" length="32"^>WUP-N-%PRODUCTCODE%^</product_code^>>>meta.xml
echo   ^<content_platform type="string" length="32"^>WUP^</content_platform^>>>meta.xml
echo   ^<company_code type="string" length="8"^>0001^</company_code^>>>meta.xml
echo   ^<mastering_date type="string" length="32"^>^</mastering_date^>>>meta.xml
echo   ^<logo_type type="unsignedInt" length="4"^>0^</logo_type^>>>meta.xml
echo   ^<app_launch_type type="hexBinary" length="4"^>00000000^</app_launch_type^>>>meta.xml
echo   ^<invisible_flag type="hexBinary" length="4"^>00000000^</invisible_flag^>>>meta.xml
echo   ^<no_managed_flag type="hexBinary" length="4"^>00000000^</no_managed_flag^>>>meta.xml
echo   ^<no_event_log type="hexBinary" length="4"^>00000000^</no_event_log^>>>meta.xml
echo   ^<no_icon_database type="hexBinary" length="4"^>00000000^</no_icon_database^>>>meta.xml
echo   ^<launching_flag type="hexBinary" length="4"^>00000005^</launching_flag^>>>meta.xml
echo   ^<install_flag type="hexBinary" length="4"^>00000000^</install_flag^>>>meta.xml
echo   ^<closing_msg type="unsignedInt" length="4"^>0^</closing_msg^>>>meta.xml
echo   ^<title_version type="unsignedInt" length="4"^>16^</title_version^>>>meta.xml
echo   ^<title_id type="hexBinary" length="8"^>000500001337%TITLEID%^</title_id^>>>meta.xml
echo   ^<group_id type="hexBinary" length="4"^>00001337^</group_id^>>>meta.xml
echo   ^<boss_id type="hexBinary" length="8"^>0000000000000000^</boss_id^>>>meta.xml
echo   ^<os_version type="hexBinary" length="8"^>000500101000400A^</os_version^>>>meta.xml
echo   ^<app_size type="hexBinary" length="8"^>0000000000000000^</app_size^>>>meta.xml
echo   ^<common_save_size type="hexBinary" length="8"^>0000000000000000^</common_save_size^>>>meta.xml
echo   ^<account_save_size type="hexBinary" length="8"^>0000000004000000^</account_save_size^>>>meta.xml
echo   ^<common_boss_size type="hexBinary" length="8"^>0000000000000000^</common_boss_size^>>>meta.xml
echo   ^<account_boss_size type="hexBinary" length="8"^>0000000000000000^</account_boss_size^>>>meta.xml
echo   ^<save_no_rollback type="unsignedInt" length="4"^>0^</save_no_rollback^>>>meta.xml
echo   ^<join_game_id type="hexBinary" length="4"^>00000000^</join_game_id^>>>meta.xml
echo   ^<join_game_mode_mask type="hexBinary" length="8"^>0000000000000000^</join_game_mode_mask^>>>meta.xml
echo   ^<bg_daemon_enable type="unsignedInt" length="4"^>1^</bg_daemon_enable^>>>meta.xml
echo   ^<olv_accesskey type="unsignedInt" length="4"^>1977281461^</olv_accesskey^>>>meta.xml
echo   ^<wood_tin type="unsignedInt" length="4"^>0^</wood_tin^>>>meta.xml
echo   ^<e_manual type="unsignedInt" length="4"^>1^</e_manual^>>>meta.xml
echo   ^<e_manual_version type="unsignedInt" length="4"^>1^</e_manual_version^>>>meta.xml
echo   ^<region type="hexBinary" length="4"^>00000004^</region^>>>meta.xml
echo   ^<pc_cero type="unsignedInt" length="4"^>128^</pc_cero^>>>meta.xml
echo   ^<pc_esrb type="unsignedInt" length="4"^>6^</pc_esrb^>>>meta.xml
echo   ^<pc_bbfc type="unsignedInt" length="4"^>192^</pc_bbfc^>>>meta.xml
echo   ^<pc_usk type="unsignedInt" length="4"^>0^</pc_usk^>>>meta.xml
echo   ^<pc_pegi_gen type="unsignedInt" length="4"^>3^</pc_pegi_gen^>>>meta.xml
echo   ^<pc_pegi_fin type="unsignedInt" length="4"^>192^</pc_pegi_fin^>>>meta.xml
echo   ^<pc_pegi_prt type="unsignedInt" length="4"^>4^</pc_pegi_prt^>>>meta.xml
echo   ^<pc_pegi_bbfc type="unsignedInt" length="4"^>3^</pc_pegi_bbfc^>>>meta.xml
echo   ^<pc_cob type="unsignedInt" length="4"^>0^</pc_cob^>>>meta.xml
echo   ^<pc_grb type="unsignedInt" length="4"^>128^</pc_grb^>>>meta.xml
echo   ^<pc_cgsrr type="unsignedInt" length="4"^>128^</pc_cgsrr^>>>meta.xml
echo   ^<pc_oflc type="unsignedInt" length="4"^>0^</pc_oflc^>>>meta.xml
echo   ^<pc_reserved0 type="unsignedInt" length="4"^>192^</pc_reserved0^>>>meta.xml
echo   ^<pc_reserved1 type="unsignedInt" length="4"^>192^</pc_reserved1^>>>meta.xml
echo   ^<pc_reserved2 type="unsignedInt" length="4"^>192^</pc_reserved2^>>>meta.xml
echo   ^<pc_reserved3 type="unsignedInt" length="4"^>192^</pc_reserved3^>>>meta.xml
echo   ^<ext_dev_nunchaku type="unsignedInt" length="4"^>0^</ext_dev_nunchaku^>>>meta.xml
echo   ^<ext_dev_classic type="unsignedInt" length="4"^>0^</ext_dev_classic^>>>meta.xml
echo   ^<ext_dev_urcc type="unsignedInt" length="4"^>0^</ext_dev_urcc^>>>meta.xml
echo   ^<ext_dev_board type="unsignedInt" length="4"^>0^</ext_dev_board^>>>meta.xml
echo   ^<ext_dev_usb_keyboard type="unsignedInt" length="4"^>0^</ext_dev_usb_keyboard^>>>meta.xml
echo   ^<ext_dev_etc type="unsignedInt" length="4"^>0^</ext_dev_etc^>>>meta.xml
echo   ^<ext_dev_etc_name type="string" length="512"^>^</ext_dev_etc_name^>>>meta.xml
echo   ^<eula_version type="unsignedInt" length="4"^>0^</eula_version^>>>meta.xml
echo   ^<drc_use type="unsignedInt" length="4"^>2^</drc_use^>>>meta.xml
echo   ^<network_use type="unsignedInt" length="4"^>1^</network_use^>>>meta.xml
echo   ^<online_account_use type="unsignedInt" length="4"^>0^</online_account_use^>>>meta.xml
echo   ^<direct_boot type="unsignedInt" length="4"^>0^</direct_boot^>>>meta.xml
echo   ^<reserved_flag0 type="hexBinary" length="4"^>00010001^</reserved_flag0^>>>meta.xml
echo   ^<reserved_flag1 type="hexBinary" length="4"^>00000000^</reserved_flag1^>>>meta.xml
echo   ^<reserved_flag2 type="hexBinary" length="4"^>00000000^</reserved_flag2^>>>meta.xml
echo   ^<reserved_flag3 type="hexBinary" length="4"^>00000000^</reserved_flag3^>>>meta.xml
echo   ^<reserved_flag4 type="hexBinary" length="4"^>00000000^</reserved_flag4^>>>meta.xml
echo   ^<reserved_flag5 type="hexBinary" length="4"^>00000000^</reserved_flag5^>>>meta.xml
echo   ^<reserved_flag6 type="hexBinary" length="4"^>00000003^</reserved_flag6^>>>meta.xml
echo   ^<reserved_flag7 type="hexBinary" length="4"^>00000001^</reserved_flag7^>>>meta.xml
IF %LINEDECIDE%==2 (
echo   ^<longname_ja type="string" length="512"^>%GAMENAME1%>>meta.xml
echo %GAMENAME2%^</longname_ja^>>>meta.xml
echo   ^<longname_en type="string" length="512"^>%GAMENAME1%>>meta.xml
echo %GAMENAME2%^</longname_en^>>>meta.xml
echo   ^<longname_fr type="string" length="512"^>%GAMENAME1%>>meta.xml
echo %GAMENAME2%^</longname_fr^>>>meta.xml
echo   ^<longname_de type="string" length="512"^>%GAMENAME1%>>meta.xml
echo %GAMENAME2%^</longname_de^>>>meta.xml
echo   ^<longname_it type="string" length="512"^>%GAMENAME1%>>meta.xml
echo %GAMENAME2%^</longname_it^>>>meta.xml
echo   ^<longname_es type="string" length="512"^>%GAMENAME1%>>meta.xml
echo %GAMENAME2%^</longname_es^>>>meta.xml
echo   ^<longname_zhs type="string" length="512"^>%GAMENAME1%>>meta.xml
echo %GAMENAME2%^</longname_zhs^>>>meta.xml
echo   ^<longname_ko type="string" length="512"^>%GAMENAME1%>>meta.xml
echo %GAMENAME2%^</longname_ko^>>>meta.xml
echo   ^<longname_nl type="string" length="512"^>%GAMENAME1%>>meta.xml
echo %GAMENAME2%^</longname_nl^>>>meta.xml
echo   ^<longname_pt type="string" length="512"^>%GAMENAME1%>>meta.xml
echo %GAMENAME2%^</longname_pt^>>>meta.xml
echo   ^<longname_ru type="string" length="512"^>%GAMENAME1%>>meta.xml
echo %GAMENAME2%^</longname_ru^>>>meta.xml
echo   ^<longname_zht type="string" length="512"^>%GAMENAME1%>>meta.xml
echo %GAMENAME2%^</longname_zht^>>>meta.xml
)
IF %LINEDECIDE%==1 (
echo   ^<longname_ja type="string" length="512"^>%GAMENAME%^</longname_ja^>>>meta.xml
echo   ^<longname_en type="string" length="512"^>%GAMENAME%^</longname_en^>>>meta.xml
echo   ^<longname_fr type="string" length="512"^>%GAMENAME%^</longname_fr^>>>meta.xml
echo   ^<longname_de type="string" length="512"^>%GAMENAME%^</longname_de^>>>meta.xml
echo   ^<longname_it type="string" length="512"^>%GAMENAME%^</longname_it^>>>meta.xml
echo   ^<longname_es type="string" length="512"^>%GAMENAME%^</longname_es^>>>meta.xml
echo   ^<longname_zhs type="string" length="512"^>%GAMENAME%^</longname_zhs^>>>meta.xml
echo   ^<longname_ko type="string" length="512"^>%GAMENAME%^</longname_ko^>>>meta.xml
echo   ^<longname_nl type="string" length="512"^>%GAMENAME%^</longname_nl^>>>meta.xml
echo   ^<longname_pt type="string" length="512"^>%GAMENAME%^</longname_pt^>>>meta.xml
echo   ^<longname_ru type="string" length="512"^>%GAMENAME%^</longname_ru^>>>meta.xml
echo   ^<longname_zht type="string" length="512"^>%GAMENAME%^</longname_zht^>>>meta.xml
)
echo   ^<shortname_ja type="string" length="256"^>%GAMENAME%^</shortname_ja^>>>meta.xml
echo   ^<shortname_en type="string" length="256"^>%GAMENAME%^</shortname_en^>>>meta.xml
echo   ^<shortname_fr type="string" length="256"^>%GAMENAME%^</shortname_fr^>>>meta.xml
echo   ^<shortname_de type="string" length="256"^>%GAMENAME%^</shortname_de^>>>meta.xml
echo   ^<shortname_it type="string" length="256"^>%GAMENAME%^</shortname_it^>>>meta.xml
echo   ^<shortname_es type="string" length="256"^>%GAMENAME%^</shortname_es^>>>meta.xml
echo   ^<shortname_zhs type="string" length="256"^>%GAMENAME%^</shortname_zhs^>>>meta.xml
echo   ^<shortname_ko type="string" length="256"^>%GAMENAME%^</shortname_ko^>>>meta.xml
echo   ^<shortname_nl type="string" length="256"^>%GAMENAME%^</shortname_nl^>>>meta.xml
echo   ^<shortname_pt type="string" length="256"^>%GAMENAME%^</shortname_pt^>>>meta.xml
echo   ^<shortname_ru type="string" length="256"^>%GAMENAME%^</shortname_ru^>>>meta.xml
echo   ^<shortname_zht type="string" length="256"^>%GAMENAME%^</shortname_zht^>>>meta.xml
echo   ^<publisher_ja type="string" length="256"^>Nintendo^</publisher_ja^>>>meta.xml
echo   ^<publisher_en type="string" length="256"^>Nintendo^</publisher_en^>>>meta.xml
echo   ^<publisher_fr type="string" length="256"^>Nintendo^</publisher_fr^>>>meta.xml
echo   ^<publisher_de type="string" length="256"^>Nintendo^</publisher_de^>>>meta.xml
echo   ^<publisher_it type="string" length="256"^>Nintendo^</publisher_it^>>>meta.xml
echo   ^<publisher_es type="string" length="256"^>Nintendo^</publisher_es^>>>meta.xml
echo   ^<publisher_zhs type="string" length="256"^>Nintendo^</publisher_zhs^>>>meta.xml
echo   ^<publisher_ko type="string" length="256"^>Nintendo^</publisher_ko^>>>meta.xml
echo   ^<publisher_nl type="string" length="256"^>Nintendo^</publisher_nl^>>>meta.xml
echo   ^<publisher_pt type="string" length="256"^>Nintendo^</publisher_pt^>>>meta.xml
echo   ^<publisher_ru type="string" length="256"^>Nintendo^</publisher_ru^>>>meta.xml
echo   ^<publisher_zht type="string" length="256"^>Nintendo^</publisher_zht^>>>meta.xml
echo   ^<add_on_unique_id0 type="hexBinary" length="4"^>00000000^</add_on_unique_id0^>>>meta.xml
echo   ^<add_on_unique_id1 type="hexBinary" length="4"^>00000000^</add_on_unique_id1^>>>meta.xml
echo   ^<add_on_unique_id2 type="hexBinary" length="4"^>00000000^</add_on_unique_id2^>>>meta.xml
echo   ^<add_on_unique_id3 type="hexBinary" length="4"^>00000000^</add_on_unique_id3^>>>meta.xml
echo   ^<add_on_unique_id4 type="hexBinary" length="4"^>00000000^</add_on_unique_id4^>>>meta.xml
echo   ^<add_on_unique_id5 type="hexBinary" length="4"^>00000000^</add_on_unique_id5^>>>meta.xml
echo   ^<add_on_unique_id6 type="hexBinary" length="4"^>00000000^</add_on_unique_id6^>>>meta.xml
echo   ^<add_on_unique_id7 type="hexBinary" length="4"^>00000000^</add_on_unique_id7^>>>meta.xml
echo   ^<add_on_unique_id8 type="hexBinary" length="4"^>00000000^</add_on_unique_id8^>>>meta.xml
echo   ^<add_on_unique_id9 type="hexBinary" length="4"^>00000000^</add_on_unique_id9^>>>meta.xml
echo   ^<add_on_unique_id10 type="hexBinary" length="4"^>00000000^</add_on_unique_id10^>>>meta.xml
echo   ^<add_on_unique_id11 type="hexBinary" length="4"^>00000000^</add_on_unique_id11^>>>meta.xml
echo   ^<add_on_unique_id12 type="hexBinary" length="4"^>00000000^</add_on_unique_id12^>>>meta.xml
echo   ^<add_on_unique_id13 type="hexBinary" length="4"^>00000000^</add_on_unique_id13^>>>meta.xml
echo   ^<add_on_unique_id14 type="hexBinary" length="4"^>00000000^</add_on_unique_id14^>>>meta.xml
echo   ^<add_on_unique_id15 type="hexBinary" length="4"^>00000000^</add_on_unique_id15^>>>meta.xml
echo   ^<add_on_unique_id16 type="hexBinary" length="4"^>00000000^</add_on_unique_id16^>>>meta.xml
echo   ^<add_on_unique_id17 type="hexBinary" length="4"^>00000000^</add_on_unique_id17^>>>meta.xml
echo   ^<add_on_unique_id18 type="hexBinary" length="4"^>00000000^</add_on_unique_id18^>>>meta.xml
echo   ^<add_on_unique_id19 type="hexBinary" length="4"^>00000000^</add_on_unique_id19^>>>meta.xml
echo   ^<add_on_unique_id20 type="hexBinary" length="4"^>00000000^</add_on_unique_id20^>>>meta.xml
echo   ^<add_on_unique_id21 type="hexBinary" length="4"^>00000000^</add_on_unique_id21^>>>meta.xml
echo   ^<add_on_unique_id22 type="hexBinary" length="4"^>00000000^</add_on_unique_id22^>>>meta.xml
echo   ^<add_on_unique_id23 type="hexBinary" length="4"^>00000000^</add_on_unique_id23^>>>meta.xml
echo   ^<add_on_unique_id24 type="hexBinary" length="4"^>00000000^</add_on_unique_id24^>>>meta.xml
echo   ^<add_on_unique_id25 type="hexBinary" length="4"^>00000000^</add_on_unique_id25^>>>meta.xml
echo   ^<add_on_unique_id26 type="hexBinary" length="4"^>00000000^</add_on_unique_id26^>>>meta.xml
echo   ^<add_on_unique_id27 type="hexBinary" length="4"^>00000000^</add_on_unique_id27^>>>meta.xml
echo   ^<add_on_unique_id28 type="hexBinary" length="4"^>00000000^</add_on_unique_id28^>>>meta.xml
echo   ^<add_on_unique_id29 type="hexBinary" length="4"^>00000000^</add_on_unique_id29^>>>meta.xml
echo   ^<add_on_unique_id30 type="hexBinary" length="4"^>00000000^</add_on_unique_id30^>>>meta.xml
echo   ^<add_on_unique_id31 type="hexBinary" length="4"^>00000000^</add_on_unique_id31^>>>meta.xml
echo ^</menu^>>>meta.xml
SLEEP 1
cls

:: INJECTING IMAGES
:InjectingImages
cd ..
cd ..
cd ..
cd ..
cd png2tga
echo Converting images to TGA...
png2tgacmd.exe -i iconTex.png --width=128 --height=128 --tga-bpp=32 --tga-compression=none
png2tgacmd.exe -i bootTvTex.png --width=1280 --height=720 --tga-bpp=24 --tga-compression=none
png2tgacmd.exe -i bootDrcTex.png --width=854 --height=480 --tga-bpp=24 --tga-compression=none
IF EXIST bootLogoTex.png (png2tgacmd.exe -i bootLogoTex.png --width=170 --height=42 --tga-bpp=32 --tga-compression=none)
title Injectiine [NDS]
del /f /q iconTex.png
del /f /q bootTvTex.png
del /f /q bootDrcTex.png
del /f /q bootLogoTex.png
MetaVerifiy.py
cls
echo Moving images to meta folder...
move iconTex.tga ..\CONSOLES\NDS\WORKDIR\meta
move bootTvTex.tga ..\CONSOLES\NDS\WORKDIR\meta
move bootDrcTex.tga ..\CONSOLES\NDS\WORKDIR\meta
2>NUL move bootLogoTex.tga ..\CONSOLES\NDS\WORKDIR\meta
del ..\CONSOLES\NDS\WORKDIR\fnr.exe
cls

:PackPrompt
cls
echo Do you want to pack the game using NUSPacker?
echo If you don't wish to, the game will be created in Loadiine format.
set /p PACKDECIDE=[Y/N:] 
IF /i "%PACKDECIDE%"=="n" (GOTO:LoadiinePack)
IF /i "%PACKDECIDE%"=="y" (GOTO:PackGame)
GOTO:PackPrompt

:LoadiinePack
cls
cd ../CONSOLES/NDS
cd ..
move NDS\WORKDIR ..\..\Output\"[NDS] %GAMENAME% [%PRODUCTCODE%]"
GOTO:FinalCheckLoadiine

:: PACK GAME
:PackGame
echo Packing game...
cd ../CONSOLES/NDS
cd ..
move NDS\WORKDIR NDS\NUSPacker\WORKDIR
cd NDS
cd NUSPacker
java -jar NUSPacker.jar -in WORKDIR -out "[NDS] %GAMENAME% (000500001337%TITLEID%)"
rd /s /q tmp
rd /s /q WORKDIR
rd /s /q output
move "[NDS] %GAMENAME% (000500001337%TITLEID%)" ..\..\..\..\Output

:: Final check if game exists
:FinalCheck
cd ..\..\..\..\Output
IF NOT EXIST "[NDS] %GAMENAME% (000500001337%TITLEID%)" GOTO:GameError
GOTO:GameComplete

:FinalCheckLoadiine
cd ..\..\Output
IF NOT EXIST "[NDS] %GAMENAME% [%PRODUCTCODE%]" GOTO:LoadiineError
GOTO:GameComplete

:GameComplete
cls
echo ::::::::::::::::::::::
echo ::INJECTION COMPLETE::
echo ::::::::::::::::::::::
echo.
echo A folder has been created named
IF /i "%PACKDECIDE%"=="y" echo "[NDS] %GAMENAME% (000500001337%TITLEID%)"
IF /i "%PACKDECIDE%"=="n" echo "[NDS] %GAMENAME% [%PRODUCTCODE%]"
echo in the Output directory with the injected game. You can install this using
echo WUP Installer GX2, WUP Installer Y Mod or System Config Tool.
echo.
echo It is recommended to install to USB in case of game corruption.
echo.
echo Press any key to exit.
pause>NUL
exit

:: ERRORS

:LastChance
IF NOT EXIST *.srl GOTO:404ROMnotFound

:404ROMnotFound
cls
echo :::::::::
echo ::ERROR::
echo :::::::::
echo.
echo NDS ROM not found.
echo.
echo Aborting in five seconds.
SLEEP 5
exit

:404ImagesNotFound
cls
echo :::::::::
echo ::ERROR::
echo :::::::::
echo.
echo Images not found.
echo.
echo Make sure you have the following images in the Files directory:
echo bootTvTex.png (1280 x 720)
echo iconTex.png (128 x 128)
echo.
echo Aborting in five seconds.
SLEEP 5
exit

:LoadiineError
cls
echo :::::::::
echo ::ERROR::
echo :::::::::
echo.
echo Failed to create a Loadiine package.
echo.
echo Aborting in five seconds.
SLEEP 5
exit

:GameError
cls
echo :::::::::
echo ::ERROR::
echo :::::::::
echo.
echo Failed to create a WUP package.
echo.
echo Aborting in five seconds.
SLEEP 5
exit

:ROBOFAIL
cls
echo :::::::::
echo ::ERROR::
echo :::::::::
echo.
echo Robocopy failed to create a working directory with the base files.
echo.
echo Aborting in five seconds.
SLEEP 5
exit

:InternetSucks
cls
echo :::::::::
echo ::ERROR::
echo :::::::::
echo.
echo Internet connection test failed.
echo.
echo Aborting in five seconds.
SLEEP 5
exit
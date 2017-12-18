::::::::::::::::::::
::INJECTIINE v1.23::
::::::::::::::::::::

Injectiine is a Wii U VC batch injector by CatmanFan.

== WHAT MAKES THIS USABLE ==
-This actually works. Every console available throws out a functionable VC inject. Just make sure to check the GBAtemp wiki compatibility lists first.

-Support for multi-line titles!

-Downloadable bases (NOTE: You will need the title key of the base you're downloading, the Wii U Common Key, and an Internet connection.)

-Supports decrypted base supplied alongside images and ROM (NOTE: You will need the Wii U Common Key.)

-Define custom options for custom INIs when injecting N64 VC

-Define custom INI/ROM name when injecting N64 VC (e.g. Undop0.599, UNMSE.714, UNPSJ.123, etc.)

-You can even use a .ini supplied alongside images and ROM, if you will

-Automatically converts *.n64 and *.v64 ROMs to *.z64 format

-Supports custom GamePad/TV backgrounds for NDS VC

-Supports custom bootSound, bootTvTex, bootDrcTex, bootLogoTex and iconTex

-Includes MetaVerify and automatically runs it when converting images to TGA

== HOW TO USE ==
Using this injector is very simple.

You will need the following files:
-A ROM
-iconTex.png (128 x 128)
-bootTvTex.png (1280 x 720)

You can also use these files, although they are optional and not recommended:
-bootDrcTex.png (854 x 480)
-bootLogoTex.png (170 x 42)
-A decrypted base folder (should be named "Base")
-A config .ini file [N64]
-drcback.png (854 x 480) [NDS]
-nds1st_31p.png (854 x 480) [NDS]
-nds1st_31p_tv.png (1280 x 720) [NDS]
-tvback.png (1280 x 720) [NDS]

Any files that you use, including the recommended ones, should be placed in the Files directory.

Once you open Injectiine, you will be prompted for a console. Select the one that corresponds to the game you're injecting (e.g. if you're injecting a NES game type 1 for NES; 2 for SNES, etc.). You will be prompted to select a base. If you have selected a downloadable base for use, you will need to enter the title key for the base and the Wii U Common Key; otherwise, if you have chosen to use a base from the Files folder, you can only enter the Common Key. Injectiine will then save the aforementioned value(s) for future use so you don't have to enter them again.

You will then be asked if the game name uses one or two lines. The next step is to input the game name (or each game name line individually if your game's title uses two lines; e.g. type "Super Mario 64" first, then "Last Impact"). You can then input a product code and title ID, and then be prompted to create the inject before proceeding.

If you choose to inject your game, the program goes through the process of downloading the base files/copying the base to a work directory, injecting the ROM (although you will have to go through some INI shittake mushrooms if you're injecting an N64 ROM), and generating the app.xml and meta.xml files before converting your images to TGA format. Once MetaVerify is opened to check the TGA files for Wii U console use, you will need to press Enter to continue. Injectiine will then prompt if you want to pack your injected game in WUP installable format or Loadiine format, and will dump the game in the Output directory.

== OTHER NOTES ==
Generated title ID is 1337xxxx.

ALWAYS INSTALL TO USB IN CASE OF GAME CORRUPTION!

== DISCLAIMER ==
I do not own any of the tools packaged in this application. They all belong to their respective owners. Some of these instructions may not be detailed precisely so don't throw any hate comments at me lol.
@echo off
title Toontown Rewritten Client
cd ../../

rem Read the contents of PPYTHON_PATH into %PPYTHON_PATH%:
set /P PPYTHON_PATH=<PPYTHON_PATH

set TTR_PLAYCOOKIE=Username4
set TTR_GAMESERVER=127.0.0.1

:main
"C:\Panda3D-1.11.0-x64\python\python.exe" -m tools.GUITesting
pause
goto :main
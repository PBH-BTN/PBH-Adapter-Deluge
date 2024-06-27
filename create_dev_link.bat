@echo off
set BASEDIR=%~dp0
set BASEDIR=%BASEDIR:~0,-1%
if [%1]==[] (
    set CONFIG_DIR=C:\Users\strluck\AppData\Roaming\deluge
) else (
    set CONFIG_DIR=%1
)
if not exist %CONFIG_DIR%\plugins (
    echo Config dir %CONFIG_DIR% is either not a directory or is not a proper deluge config directory. Exiting
    exit /b 1
)
cd %BASEDIR%
if not exist %BASEDIR%\temp (
    md %BASEDIR%\temp
)
set PYTHONPATH=%BASEDIR%/temp
C:\Users\strluck\AppData\Local\Programs\Python\Python310\python.exe setup.py build develop --install-dir %BASEDIR%\temp
copy "%BASEDIR%\temp\*.egg-link" "%CONFIG_DIR%\plugins"
rd /s /q %BASEDIR%\temp

@ECHO OFF
SET curdir=%cd%
CD %~dp0

IF "%1" == "bootstrap" GOTO :Bootstrap
IF "%1" == "install" GOTO :Install
IF "%1" == "test" GOTO :Test

GOTO :Return

:: Function to bootstrap the source code
:Bootstrap
  CALL python setup.py bootstrap
  IF NOT %ERRORLEVEL% == 0 GOTO :Return

:: Function to install the program
:Install
  CALL python setup.py clean --all
  CALL python setup.py install
  IF NOT %ERRORLEVEL% == 0 GOTO :Return

:: Function to test the program
:Test
  CALL python setup.py cleantest
  CALL python setup.py test

:Return
  CD %curdir%
  EXIT /B %ERRORLEVEL%

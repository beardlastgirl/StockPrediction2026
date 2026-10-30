@echo off
setlocal
set "ROOT=%~dp0"
set "PYTHONWARNINGS=ignore"
"%ROOT%.venv\Scripts\python.exe" -m eventstudy %*

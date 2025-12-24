@echo off
REM Launch Personal Automation Engine with GUI (silent mode)

REM Check if config exists, if not run setup
if not exist "config\config.yaml" (
    start /wait python setup.py
)

REM Run the GUI without console window
start "" pythonw main_gui.py

REM Exit immediately without waiting
exit

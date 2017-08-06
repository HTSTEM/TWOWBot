@echo off
cd ..
:a

where /q python3
IF ERRORLEVEL 1 (
    python bot.py
) ELSE (
    python3 bot.py
)
goto a
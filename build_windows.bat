@echo off
cd /d "%~dp0"
where py >nul 2>nul && (set PY=py) || (set PY=python)
%PY% -m pip install pynput pyinstaller
%PY% -m PyInstaller --noconfirm --onefile --noconsole --name "Auto Typer" --icon auto_typer.ico auto_typer.py
echo.
echo Built: dist\Auto Typer.exe
pause

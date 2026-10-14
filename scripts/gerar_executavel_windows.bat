@echo off
setlocal
cd /d "%~dp0\.."
chcp 65001 >nul

echo ========================================
echo  Gerador de executaveis para Windows
echo ========================================
where py >nul 2>&1
if errorlevel 1 (
  echo Python Launcher nao encontrado. Instale Python no computador de COMPILACAO.
  exit /b 1
)

py -m pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1

py -m PyInstaller --noconfirm --clean --onedir --windowed --name GerenciadorNotas --paths "%CD%" cliente\main.py
if errorlevel 1 exit /b 1

py -m PyInstaller --noconfirm --clean --onefile --console --name ServidorNotas --distpath dist\GerenciadorNotas --paths "%CD%" servidor\app.py
if errorlevel 1 exit /b 1

if not exist "dist\GerenciadorNotas\dados" mkdir "dist\GerenciadorNotas\dados"
copy /Y servidor\dados\*.json "dist\GerenciadorNotas\dados\" >nul

echo.
echo Pronto: dist\GerenciadorNotas\GerenciadorNotas.exe
echo Copie a pasta dist\GerenciadorNotas INTEIRA para o outro computador.
echo Teste sem Python instalado antes da entrega.
pause

@echo off
chcp 65001 >nul
rem Abre o Lab SQ Jarvis (JV-V01, dados simulados). Para fechar, feche a janela do programa.
cd /d "%~dp0"

rem Procura o Python (py launcher ou python)
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
  where python >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo.
  echo  [PROBLEMA] O Python nao foi encontrado neste computador.
  echo  Peca ao Claude: "instala o Python 3.13 para mim" e marque "Add Python to PATH".
  echo.
  pause
  exit /b 1
)

rem O programa precisa do Python 3.11 a 3.14
%PY% -c "import sys; sys.exit(0 if (3,11) <= sys.version_info[:2] <= (3,14) else 1)" >nul 2>nul
if errorlevel 1 (
  echo.
  echo  [PROBLEMA] A versao do Python instalada nao serve. O programa precisa do Python 3.11 a 3.14.
  echo  Peca ao Claude: "instala o Python 3.13 para mim".
  echo.
  pause
  exit /b 1
)

if not exist .venv\Scripts\python.exe (
  echo  Preparando o ambiente pela primeira vez - leva alguns minutos e precisa de internet...
  %PY% -m venv .venv
  if errorlevel 1 (
    echo.
    echo  [PROBLEMA] Nao consegui criar o ambiente do programa. Mostre esta janela ao Claude.
    echo.
    pause
    exit /b 1
  )
)

if not exist .venv\instalado-v01.txt (
  echo  Instalando as pecas do programa - so na primeira vez...
  call .venv\Scripts\python.exe -m pip install --disable-pip-version-check -r requirements.txt
  if errorlevel 1 (
    echo.
    echo  [PROBLEMA] Nao consegui instalar as pecas. Verifique a internet e tente de novo.
    echo  Se continuar, mostre esta janela ao Claude.
    echo.
    pause
    exit /b 1
  )
  echo ok> .venv\instalado-v01.txt
)

set "PYTHONPATH=%~dp0src"
echo.
echo  Abrindo o Lab SQ Jarvis - demonstracao com dados SIMULADOS.
echo  Seus dados ficam em %%LOCALAPPDATA%%\LabSQJarvis. Feche esta janela para encerrar.
echo.
call .venv\Scripts\python.exe -m jarvis
if errorlevel 1 (
  echo.
  echo  [PROBLEMA] O programa parou com erro. Mostre esta janela ao Claude.
  pause
)

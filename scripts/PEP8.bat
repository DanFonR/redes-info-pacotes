@echo off

REM Obtém o diretório do script e volta um nível
SET SCRIPT_DIR=%~dp0
SET SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
PUSHD %SCRIPT_DIR%\..

REM Verifica se os pacotes estão instalados
for %%P in (isort black flake8) do (
    pip show %%P >nul 2>&1
    if errorlevel 1 (
        echo %%P nao esta instalado
        POPD
        exit /b 1
    )
)

echo Rodando isort...
isort .

echo Rodando black...
black .

echo Rodando flake8...
flake8 .

echo Concluído! Código formatado e verificado.

POPD

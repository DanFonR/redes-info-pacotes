@ECHO OFF

:: Obtém o diretório do script e volta um nível
SET SCRIPT_DIR=%~dp0
SET SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
PUSHD %SCRIPT_DIR%\..

:: Verifica se os pacotes estão instalados
FOR %%P IN (isort black flake8) do (
    pip show %%P >NUL 2>&1
    IF ERRORLEVEL 1 (
        ECHO %%P nao esta instalado
        POPD
        EXIT /B 1
    )
)

ECHO Rodando isort...
isort .

ECHO Rodando black...
black --line-length 79 .

ECHO Rodando flake8...
flake8 .

ECHO Concluído! Código formatado e verificado.

POPD

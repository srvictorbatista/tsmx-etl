@echo off

:: Define o container
set "container=etl_tsmx"


:: Verifica se o script está rodando como administrador
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Este script precisa ser executado como administrador
    PAUSE >NUL
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Checa build
docker inspect -f "{{.State.Running}}" %container% 2>nul | findstr "true" >nul && goto BASH

:: START!
:: CLS&docker-compose up --build
START cmd /k "docker-compose up --build"&CLS

:BASH
:: Ajusta a janela, mantendo a rolagem
mode con: cols=220 lines=50 & powershell -command "$Host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size(220,30000)"

title %container%

:: Executa o docker exec
:LOOP
docker exec -it %container% bash

:: Após sair do bash, espera
CLS&echo.
echo Esperando bash...
timeout /t 60 /nobreak >nul

:: Volta para o loop
CLS&goto LOOP








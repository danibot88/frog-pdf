@echo off
TITLE FrogPDF - Inicializando Sistema Seguro...
echo Verificando servicos locais...

:: Verifica se o Ollama esta rodando, se nao estiver, tenta inicializa-lo em segundo plano
tasklist /FI "IMAGENAME eq ollama.exe" 2>NENHUM | find /I "ollama.exe">NENHUM
if errorlevel 1 (
    echo O Ollama nao esta ativo. Iniciando Ollama localmente...
    start /min ollama serve
    timeout /t 5 >nul
)

echo Iniciando FrogPDF...
start http://localhost:8501
dist\FrogPDF\FrogPDF.exe

pause
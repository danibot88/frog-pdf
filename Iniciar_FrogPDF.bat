@echo off
TITLE FrogPDF - Assistente Local de Documentos
color 0A
cls

echo ========================================================
echo          INICIANDO FROGPDF (Modo 100%% Seguro)
echo ========================================================
echo.

:: 1. Verifica se o Ollama esta rodando, se nao, inicia em segundo plano
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I "ollama.exe">NUL
if errorlevel 1 (
    echo [1/3] O Ollama nao esta ativo. Iniciando Ollama localmente...
    start /min ollama serve
    timeout /t 4 >nul
) else (
    echo [1/3] Servico Ollama ja esta rodando em segundo plano.
)

:: 2. Vai para a pasta correta do projeto
cd /d "%~dp0"

:: 3. Abre o navegador na porta do Streamlit e inicia o app
echo [2/3] Abrindo interface no navegador...
start http://localhost:8501

echo [3/3] Iniciando aplicacao Python...
python -m streamlit run app.py --server.headless=true

pause
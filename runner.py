import os
import sys
import subprocess

if __name__ == "__main__":
    # Descobre o diretório real onde o executável está rodando
    if getattr(sys, 'frozen', False):
        current_dir = sys._MEIPASS
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))

    app_path = os.path.join(current_dir, "app.py")

    # Executa o Streamlit chamando o processo de forma estável
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path, "--global.developmentMode=false"])
    except Exception as e:
        print(f"Erro crítico ao iniciar o FrogPDF: {e}")
        input("Pressione Enter para fechar...")
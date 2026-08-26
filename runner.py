
import os
import sys
import streamlit.web.bootstrap

if __name__ == "__main__":
    # Garante que o caminho base aponte para a pasta correta do executável
    if getattr(sys, 'frozen', False):
        os.chdir(sys._MEIPASS)
    
    # Configura os parâmetros para rodar o app.py do Streamlit embutido
    sys.argv = [
        "streamlit",
        "run",
        "app.py",
        "--global.developmentMode=false",
    ]
    
    streamlit.web.bootstrap.run()
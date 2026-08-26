import os
import sys
import streamlit.web.bootstrap

if __name__ == "__main__":
    # Define o diretório de trabalho correto dependendo se roda via script ou .exe compilado
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    os.chdir(base_path)
    sys.path.append(base_path)

    # Caminho absoluto para a aplicação principal
    target_app = os.path.join(base_path, "app.py")

    # Configura os argumentos de execução nativa do Streamlit
    sys.argv = [
        "streamlit",
        "run",
        target_app,
        "--global.developmentMode=false",
    ]

    try:
        # Inicia o bootstrap do Streamlit diretamente no processo atual
        streamlit.web.bootstrap.run(
            target_app,
            False,
            [],
            {}
        )
    except Exception as e:
        print(f"Erro fatal ao iniciar o FrogPDF: {e}")
        input("Pressione Enter para sair...")
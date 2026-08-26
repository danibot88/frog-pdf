
# 🐸 FrogPDF: Assistente de Documentos IA 100% Local e Seguro

O **FrogPDF** é uma aplicação desktop inteligente desenvolvida em Python e Streamlit, projetada para ler, mesclar, resumir, extrair dados e interagir via chat com documentos confidenciais (**PDF, Word, Excel, CSV**). 

O grande diferencial do FrogPDF é a sua **privacidade absoluta**: ele roda 100% offline em sua máquina local utilizando o motor de IA **Ollama (Llama 3.2)**, garantindo que nenhum dado corporativo ou sensível de clientes vaze para a nuvem.

---

## ✨ Principais Funcionalidades
- **100% Offline e Privado:** Sem chamadas de API externas ou dependência de internet. Seus dados ficam no seu computador.
- **Suporte a Múltiplos Formatos:** Leitura nativa de PDFs, arquivos do Word, planilhas Excel e CSVs.
- **OCR Integrado:** Extração automática de texto de PDFs digitalizados ou imagens (via Tesseract).
- **Gestão de Clientes e Projetos:** Separação de documentos em pastas locais por projeto, com opções de status **Ativos** e **Inativos (Referências)**.
- **Busca Semântica Local (RAG):** Faça perguntas ao chat e cruze informações entre documentos de um ou múltiplos projetos simultaneamente, com **citação obrigatória de fontes**.
- **Extração de Dados-Chave:** Mapeamento instantâneo de entidades (CNPJ, valores, datas e partes envolvidas) em tabelas limpas.
- **Central de Exportação:** Exporte análises e relatórios consolidados para **Word (.docx)**, **PDF (.pdf)** e **Excel (.xlsx)**.

---

## 📂 Estrutura do Projeto
```text
frog_pdf/
│
├── app.py                     # Interface principal do usuário (Streamlit)
├── runner.py                  # Script iniciador em Python
├── frog.ico                   # Ícone personalizado da aplicação
├── requirements.txt           # Dependências do projeto
├── Iniciar_FrogPDF.bat        # Atalho inteligente para iniciar o sistema no Windows
├── README.md                  # Documentação técnica
├── GUIA_USUARIO.md            # Guia simplificado para usuários finais
│
├── .streamlit/
│   └── config.toml            # Configurações de tema visual (Verde Claro / Branco)
│
├── modules/                   
│   ├── document_loader.py     # Leitor e OCR local
│   ├── ai_engine.py           # Conexão com o Ollama (Llama 3.2)
│   ├── merger.py              # Estratégias de Merge e Exportadores
│   ├── database.py            # Gestão de SQLite (Projetos e Chat)
│   └── rag_engine.py          # Motor de busca vetorial local (TF-IDF/RAG)
│
└── data/                      
    ├── uploads/               # Pastas isoladas por projeto (ignorado pelo git)
    └── frog_pdf.db            # Banco de dados local de histórico (ignorado pelo git)

#    Guia Rápido de Instalação (Desenvolvedores)
Pré-requisitos:
Python 3.10+ instalado.

Ollama instalado com o modelo padrão baixado:
ollama pull llama3.2

Tesseract OCR instalado no sistema operacional.

pip install -r requirements.txt

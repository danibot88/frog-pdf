# 🐸 FrogPDF: Secure Local AI Document Assistant

**FrogPDF** is a desktop-oriented assistant designed to read, merge, summarize, and extract tabular data from confidential documents (**PDF, Word, Excel, CSV**) completely offline. It guarantees 100% data privacy by leveraging local LLMs via **Ollama**.

---

## 📂 Project Structure

```text
frog_pdf/
│
├── app.py                     # Main Streamlit user interface
├── runner.py                  # Streamlit execution wrapper for PyInstaller
├── frog.ico                   # Custom application icon
├── requirements.txt           # Python dependencies list
├── Iniciar_FrogPDF.bat        # Windows shortcut script for end-users
├── README.md                  # Project documentation (this file)
│
├── modules/                   # Core business logic modules
│   ├── __init__.py            # Python package initializer
│   ├── document_loader.py     # Native parser & Tesseract OCR for scans
│   ├── ai_engine.py           # Local Ollama (Llama 3.2) communication engine
│   └── merger.py              # Merge strategies & Word/Excel exporters
│
└── data/                      # Local secure storage directories
    ├── uploads/               # Temporary storage for uploaded documents
    └── vector_db/             # Local ChromaDB directory for RAG/chat
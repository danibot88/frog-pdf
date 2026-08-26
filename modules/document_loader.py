
import os
import pandas as pd
import pymupdf  # Substituiu o antigo 'import fitz'
import docx     # python-docx para arquivos Word
from PIL import Image
import pytesseract

class DocumentLoader:
    """
    Class responsible for loading, extracting text, and applying OCR 
    to various document formats locally without cloud dependencies.
    """
    
    def __init__(self, tesseract_path: str = None):
        # Caminho padrão do Tesseract no Windows para evitar erros de PATH
        default_windows_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        elif os.path.exists(default_windows_path):
            pytesseract.pytesseract.tesseract_cmd = default_windows_path
        else:
            # Fallback caso esteja instalado em outro local ou configurado no PATH global
            pass

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Option 1: Extract text natively using PyMuPDF.
        Option 2: Fallback to Tesseract OCR if the page contains images/scans.
        """
        extracted_text = ""
        try:
            doc = pymupdf.open(file_path) # Atualizado para usar pymupdf
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    extracted_text += f"\n--- Page {page_num + 1} (Native) ---\n" + text
                else:
                    # Fallback para OCR caso o PDF seja uma imagem escaneada
                    pix = page.get_pixmap()
                    img_path = f"temp_page_{page_num}.png"
                    pix.save(img_path)
                    image = Image.open(img_path)
                    ocr_text = pytesseract.image_to_string(image, lang='por')
                    extracted_text += f"\n--- Page {page_num + 1} (OCR) ---\n" + ocr_text
                    if os.path.exists(img_path):
                        os.remove(img_path)
        except Exception as e:
            extracted_text += f"\nError processing PDF {file_path}: {str(e)}"
            
        return extracted_text

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extracts text paragraphs from Microsoft Word documents (.docx)."""
        try:
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            return f"Error processing DOCX {file_path}: {str(e)}"

    def extract_text_from_spreadsheet(self, file_path: str) -> str:
        """Extracts tabular data from Excel or CSV files and converts to Markdown format."""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            return df.to_markdown(index=False)
        except Exception as e:
            return f"Error processing Spreadsheet {file_path}: {str(e)}"

    def load_document(self, file_path: str) -> str:
        """Router method to choose the appropriate parser based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif ext in ['.xlsx', '.xls', '.csv']:
            return self.extract_text_from_spreadsheet(file_path)
        else:
            return f"Unsupported file format: {ext}"
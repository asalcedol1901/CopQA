import os
import pdfplumber
import pytesseract

from PIL import Image
from docx import Document

from pdf2image import convert_from_path


class DocumentReader:

    def extract_text(self, file_path):

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pdf":
            return self._read_pdf(file_path)

        elif extension in [".png", ".jpg", ".jpeg"]:
            return self._read_image(file_path)

        elif extension == ".docx":
            return self._read_docx(file_path)

        elif extension == ".txt":
            with open(file_path, encoding="utf8") as f:
                return f.read()

        else:
            raise Exception(
                f"Formato no soportado: {extension}"
            )

    def _read_docx(self, path):

        doc = Document(path)

        return "\n".join(
            p.text for p in doc.paragraphs
        )

    def _read_image(self, path):

        image = Image.open(path)

        return pytesseract.image_to_string(
            image,
            lang="spa"
        )

    def _read_pdf(self, path):

        text = ""

        # 1. Intentar extraer texto nativo del PDF
        try:

            with pdfplumber.open(path) as pdf:

                for page in pdf.pages:

                    txt = page.extract_text()

                    if txt:
                        text += txt + "\n"

        except Exception as e:

            print(
                f"Error leyendo PDF con pdfplumber: {e}"
            )

        # 2. Si el texto es poco, ejecutar OCR
        if len(text.strip()) < 1000:

            print(
                "Texto insuficiente. Ejecutando OCR..."
            )

            text = ""

            pages = convert_from_path(path)

            for page in pages:

                text += pytesseract.image_to_string(
                    page,
                    lang="spa"
                )

        return text
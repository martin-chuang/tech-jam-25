import fitz # PyMuPDF

class FileReader:
    def readPdfFile(self, file_path):
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"Error extracting text with PyMuPDF: {e}")
        return text
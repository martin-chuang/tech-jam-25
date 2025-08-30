"""File converter utility for converting various file types to markdown."""

import io
import logging
from typing import Optional

from werkzeug.datastructures import FileStorage

try:
    import fitz  # PyMuPDF for PDF files

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import docx  # python-docx for Word documents

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class FileConverter:
    """Utility class for converting files to markdown format."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def convert_to_markdown(self, file: FileStorage) -> str:
        """
        Convert uploaded file to markdown format.

        Args:
            file: FileStorage object from Flask request

        Returns:
            Markdown formatted string representation of the file content
        """
        if not file or not file.filename:
            return ""

        content_type = file.content_type
        filename = file.filename.lower()

        try:
            if content_type == "application/pdf" or filename.endswith(".pdf"):
                return self._convert_pdf_to_markdown(file)
            elif content_type in [
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ] or filename.endswith((".doc", ".docx")):
                return self._convert_docx_to_markdown(file)
            elif content_type in ["text/plain", "text/markdown"] or filename.endswith(
                (".txt", ".md")
            ):
                return self._convert_text_to_markdown(file)
            elif content_type in ["text/csv", "application/json"] or filename.endswith(
                (".csv", ".json")
            ):
                return self._convert_structured_to_markdown(file)
            else:
                self.logger.warning(f"Unsupported file type: {content_type}")
                return f"# {file.filename}\n\n*Unsupported file type: {content_type}*"

        except Exception as e:
            self.logger.error(f"Error converting file {file.filename}: {str(e)}")
            return f"# {file.filename}\n\n*Error reading file: {str(e)}*"

    def _convert_pdf_to_markdown(self, file: FileStorage) -> str:
        """Convert PDF file to markdown."""
        if not PDF_AVAILABLE:
            return f"# {file.filename}\n\n*PDF processing not available - PyMuPDF not installed*"

        try:
            # Check if file is still readable
            if file.closed:
                return f"# {file.filename}\n\n*Error processing PDF: File is closed.*"

            # Save current position and reset to beginning
            current_pos = file.tell()
            file.seek(0)

            # Read file content into bytes
            file_bytes = file.read()

            # Restore original position
            try:
                file.seek(current_pos)
            except:
                # If we can't seek back, that's ok for this use case
                pass

            if not file_bytes:
                return f"# {file.filename}\n\n*Error processing PDF: No content found.*"

            # Open PDF from bytes
            pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")

            markdown_content = f"# {file.filename}\n\n"

            for page_num in range(pdf_doc.page_count):
                page = pdf_doc[page_num]
                text = page.get_text()

                if text.strip():
                    markdown_content += f"## Page {page_num + 1}\n\n"
                    markdown_content += text.strip() + "\n\n"

            pdf_doc.close()
            return markdown_content

        except Exception as e:
            self.logger.error(f"Error processing PDF {file.filename}: {str(e)}")
            return f"# {file.filename}\n\n*Error processing PDF: {str(e)}*"

    def _convert_docx_to_markdown(self, file: FileStorage) -> str:
        """Convert Word document to markdown."""
        if not DOCX_AVAILABLE:
            return f"# {file.filename}\n\n*Word document processing not available - python-docx not installed*"

        try:
            # Read the document
            doc = docx.Document(file)

            markdown_content = f"# {file.filename}\n\n"

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    # Simple markdown conversion - could be enhanced
                    if paragraph.style.name.startswith("Heading"):
                        level = paragraph.style.name.replace("Heading ", "")
                        try:
                            level_num = int(level)
                            markdown_content += (
                                f"{'#' * (level_num + 1)} {paragraph.text}\n\n"
                            )
                        except:
                            markdown_content += f"## {paragraph.text}\n\n"
                    else:
                        markdown_content += paragraph.text + "\n\n"

            return markdown_content

        except Exception as e:
            self.logger.error(
                f"Error processing Word document {file.filename}: {str(e)}"
            )
            return f"# {file.filename}\n\n*Error processing Word document: {str(e)}*"

    def _convert_text_to_markdown(self, file: FileStorage) -> str:
        """Convert plain text or markdown file to markdown."""
        try:
            content = file.read().decode("utf-8")
            file.seek(0)  # Reset file pointer

            if file.filename.lower().endswith(".md"):
                # Already markdown
                return content
            else:
                # Plain text - wrap in markdown
                return f"# {file.filename}\n\n```\n{content}\n```"

        except Exception as e:
            self.logger.error(f"Error processing text file {file.filename}: {str(e)}")
            return f"# {file.filename}\n\n*Error processing text file: {str(e)}*"

    def _convert_structured_to_markdown(self, file: FileStorage) -> str:
        """Convert CSV or JSON files to markdown."""
        try:
            content = file.read().decode("utf-8")
            file.seek(0)  # Reset file pointer

            if file.filename.lower().endswith(".json"):
                return f"# {file.filename}\n\n```json\n{content}\n```"
            elif file.filename.lower().endswith(".csv"):
                lines = content.split("\n")
                if lines:
                    markdown_content = f"# {file.filename}\n\n"

                    # Try to create a markdown table
                    if len(lines) > 1:
                        header = lines[0].split(",")
                        markdown_content += "| " + " | ".join(header) + " |\n"
                        markdown_content += (
                            "| " + " | ".join(["---"] * len(header)) + " |\n"
                        )

                        for line in lines[1:10]:  # Show first 10 rows
                            if line.strip():
                                cells = line.split(",")
                                markdown_content += "| " + " | ".join(cells) + " |\n"

                        if len(lines) > 11:
                            markdown_content += "\n*... (showing first 10 rows)*\n"
                    else:
                        markdown_content += f"```csv\n{content}\n```"

                    return markdown_content

            return f"# {file.filename}\n\n```\n{content}\n```"

        except Exception as e:
            self.logger.error(
                f"Error processing structured file {file.filename}: {str(e)}"
            )
            return f"# {file.filename}\n\n*Error processing file: {str(e)}*"

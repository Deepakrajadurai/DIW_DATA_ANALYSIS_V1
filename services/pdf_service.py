import PyPDF2
import io
import logging
import re
from typing import Optional, Tuple

# Configure logging for better visibility of operations and errors
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFService:
    """
    A service class for extracting text from PDF files and validating PDF content.

    This class provides methods to:
    - Extract text from PDF content, handling encryption and page-specific errors.
    - Clean the extracted text to remove excessive whitespace and formatting artifacts.
    - Validate if a given byte stream is a proper PDF file.
    """

    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extract text from PDF content with improved error handling.

        Args:
            pdf_content: The content of the PDF file as bytes.

        Returns:
            A string containing the extracted and cleaned text from the PDF,
            or an empty string if extraction fails or no text is found.
        """
        if not pdf_content:
            logger.error("Empty PDF content provided. Cannot extract text.")
            return ""

        try:
            logger.info(f"Attempting to process PDF of size: {len(pdf_content)} bytes")
            
            # Create a file-like object from bytes for PyPDF2
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Check for encryption and attempt decryption
            if pdf_reader.is_encrypted:
                logger.warning("PDF is encrypted. Attempting to decrypt with an empty password.")
                try:
                    # PyPDF2's decrypt method returns True on success, False otherwise
                    if not pdf_reader.decrypt(""):
                        logger.error("Could not decrypt PDF with an empty password. Password protected PDF.")
                        return ""
                    logger.info("PDF decrypted successfully with empty password.")
                except Exception as e:
                    logger.error(f"Error during PDF decryption: {e}")
                    return ""

            # Get the number of pages in the PDF
            num_pages = len(pdf_reader.pages)
            logger.info(f"PDF has {num_pages} pages.")

            if num_pages == 0:
                logger.warning("PDF has no pages. No text to extract.")
                return ""

            extracted_text = ""
            successful_pages = 0

            # Iterate through each page to extract text
            for page_num in range(num_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text and page_text.strip():
                        extracted_text += page_text + "\n\n"  # Add double newline for paragraph separation
                        successful_pages += 1
                        logger.debug(f"Extracted {len(page_text)} characters from page {page_num + 1}.")
                    else:
                        logger.warning(f"No readable text found on page {page_num + 1}. It might be an image-only page.")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}. Skipping this page.")
                    continue
            
            logger.info(f"Successfully extracted text from {successful_pages}/{num_pages} pages.")

            if not extracted_text.strip():
                logger.error("No text could be extracted from the entire PDF. Possible reasons:")
                logger.error("  - The PDF might be entirely image-based (e.g., a scanned document).")
                logger.error("  - The PDF might contain embedded images instead of selectable text.")
                logger.error("  - The PDF file might be corrupted or malformed.")
                return ""

            # Clean up the extracted text for better readability
            cleaned_text = self._clean_text(extracted_text)
            logger.info(f"Final extracted and cleaned text length: {len(cleaned_text)} characters.")
            return cleaned_text

        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"PyPDF2 read error: {e}. This PDF might be corrupted, malformed, or in an unsupported format.")
            return ""
        except Exception as e:
            logger.error(f"An unexpected error occurred during PDF text extraction: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return ""

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing excessive whitespace and formatting artifacts.

        Args:
            text: The raw text extracted from the PDF.

        Returns:
            The cleaned string.
        """
        if not text:
            return ""

        try:
            # Replace various whitespace characters with a single space
            text = re.sub(r'\s+', ' ', text)
            
            # Replace form feed characters with newlines, then normalize newlines
            text = text.replace('\f', '\n').replace('\r', '\n')
            text = re.sub(r'\n+', '\n\n', text) # Ensure at most two newlines for paragraph breaks

            # Remove spaces before punctuation and ensure one space after (if not followed by newline)
            text = re.sub(r'\s+([,.!?;:])', r'\1', text)
            text = re.sub(r'([,.!?;:])\s+', r'\1 ', text)
            
            # Remove leading/trailing whitespace from the entire text
            text = text.strip()

            # Remove very short lines that might be artifacts (e.g., single characters, page numbers)
            # This logic keeps empty lines for paragraph breaks
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                stripped_line = line.strip()
                # Keep lines longer than 3 characters or empty lines (for paragraph separation)
                if len(stripped_line) > 3 or stripped_line == '':
                    cleaned_lines.append(stripped_line)
            text = '\n'.join(cleaned_lines)
            
            # Final pass to ensure no more than two consecutive newlines
            text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
            
            return text.strip()
        except Exception as e:
            logger.warning(f"Error cleaning text: {e}. Returning original text (stripped).")
            return text.strip()

    def validate_pdf(self, pdf_content: bytes) -> Tuple[bool, str]:
        """
        Validate if the content is a proper PDF file.

        This method performs a basic validation by checking the PDF header
        and attempting to read the number of pages.

        Args:
            pdf_content: The content of the file as bytes.

        Returns:
            A tuple: (True, "Success message") if valid,
                     (False, "Error message") if invalid.
        """
        if not pdf_content:
            return False, "Empty file content provided."

        # Basic size check: A valid PDF is usually larger than a few bytes.
        if len(pdf_content) < 100:
            return False, "File content is too small to be a valid PDF."

        # Check for the standard PDF header
        if not pdf_content.startswith(b'%PDF-'):
            return False, "File does not have a valid PDF header (%PDF- not found at beginning)."

        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Attempt to access basic properties to confirm readability
            num_pages = len(pdf_reader.pages)
            if num_pages == 0:
                return False, "PDF appears valid but contains no pages."
            
            return True, f"Valid PDF detected with {num_pages} pages."
        except PyPDF2.errors.PdfReadError as e:
            return False, f"Invalid PDF format or corrupted file: {str(e)}"
        except Exception as e:
            return False, f"An unexpected error occurred during PDF validation: {str(e)}"



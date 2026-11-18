# utils/pdf_processor.py
from pathlib import Path

from pypdf import PdfReader

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


def process_pdf(
    file_path: Path,
    original_filename: str,
    document_id: str,
    session_id: str
):

    # 1. Validate file existence
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError("PDF file does not exist.")

    # 2. Validate file extension
    if file_path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are allowed.")

    # 3. Validate file size
    file_size = file_path.stat().st_size

    max_size = settings.MAX_PDF_SIZE_MB * 1024 * 1024

    if file_size == 0:
        raise ValueError("Uploaded PDF is empty.")

    if file_size > max_size:
        raise ValueError(
            f"PDF size exceeds the limit of "
            f"{settings.MAX_PDF_SIZE_MB} MB."
        )

    # 4. Validate PDF structure and page count
    try:
        reader = PdfReader(str(file_path))

        if reader.is_encrypted:
            raise ValueError("Password-protected PDFs are not supported.")

        total_pages = len(reader.pages)

    except ValueError:
        raise

    except Exception as error:
        raise ValueError("Invalid or corrupted PDF file.") from error

    if total_pages == 0:
        raise ValueError("PDF contains no pages.")

    if total_pages > settings.MAX_PDF_PAGES:
        raise ValueError(
            f"PDF exceeds the maximum limit of "
            f"{settings.MAX_PDF_PAGES} pages."
        )

    # 5. Extract text from PDF
    try:
        loader = PyPDFLoader(str(file_path))
        pages = loader.load()

    except Exception as error:
        raise ValueError("Unable to extract text from PDF.") from error

    if not pages:
        raise ValueError("No readable pages found in PDF.")

    # 6. Remove empty pages
    pages = [
        page for page in pages
        if page.page_content.strip()
    ]

    if not pages:
        raise ValueError(
            "PDF contains no extractable text. "
            "Scanned PDFs may require OCR."
        )

    # 7. Create text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )

    # 8. Split PDF pages into chunks
    chunks = text_splitter.split_documents(pages)

    # 9. Attach metadata to every chunk
    for chunk in chunks:

        page_index = chunk.metadata.get("page", 0)

        chunk.metadata.update({
            "document_id": document_id,
            "session_id": session_id,
            "source_file": original_filename,
            "page_number": page_index + 1
        })

    if not chunks:
        raise ValueError("Unable to create text chunks from PDF.")

    return chunks
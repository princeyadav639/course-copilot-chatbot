# config.py
import os
from pathlib import Path
from dotenv import load_dotenv


# --------------------------------------------------
# 1. PROJECT DIRECTORY


BASE_DIR = Path(__file__).resolve().parents[2]


# --------------------------------------------------
# 2. LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)


# --------------------------------------------------
# 3. SETTINGS CLASS
# --------------------------------------------------

class Settings:

    # GROQ Configuration
    GROQ_API_KEY: str = (
        os.getenv("GROQ_API_KEY")
        
    )

    GEMINI_API_KEY: str = (os.getenv("GEMINI_API_KEY"))

    # LLM Configuration
    LLM_MODEL: str = os.getenv(
        "LLM_MODEL",
        "openai/gpt-oss-20b"
    )

    LLM_TEMPERATURE: float = float(
        os.getenv("LLM_TEMPERATURE", "0.2")
    )

    # Embedding Configuration
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "gemini-embedding-2"
    )

    # Storage Directories
    STORAGE_DIR: Path = BASE_DIR / "storage"

    UPLOAD_DIR: Path = STORAGE_DIR / "uploads"

    VECTOR_DB_DIR: Path = STORAGE_DIR / "vector_db"

    # PDF Configuration
    MAX_PDF_SIZE_MB: int = int(
        os.getenv("MAX_PDF_SIZE_MB", "20")
    )

    MAX_PDF_PAGES: int = int(
        os.getenv("MAX_PDF_PAGES", "200")
    )

    # Text Processing Configuration
    CHUNK_SIZE: int = int(
        os.getenv("CHUNK_SIZE", "1200")
    )

    CHUNK_OVERLAP: int = int(
        os.getenv("CHUNK_OVERLAP", "150")
    )

    # Chat History Configuration
    HISTORY_TOKEN_BUDGET: int = int(
        os.getenv("HISTORY_TOKEN_BUDGET", "6000")
    )

    MAX_HISTORY_MESSAGES: int = int(
        os.getenv("MAX_HISTORY_MESSAGES", "12")
    )

    # Retrieval Configuration
    RETRIEVER_TOP_K: int = int(
        os.getenv("RETRIEVER_TOP_K", "3")
    )

    # Application Configuration
    APP_NAME: str = "Course Copilot"

    DEBUG: bool = (
        os.getenv("DEBUG", "false").lower() == "true"
    )

    # --------------------------------------------------
    # 4. VALIDATION
    # --------------------------------------------------

    def validate_api_key(self):
        if not self.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is missing. "
                "Please add it to your .env file."
            )
    def validate_groq_api_key(self):
        if not self.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is missing. "
                "Please add it to your .env file."
            )

    def validate_settings(self):

        if self.MAX_PDF_SIZE_MB <= 0:
            raise ValueError("MAX_PDF_SIZE_MB must be positive.")

        if self.MAX_PDF_PAGES <= 0:
            raise ValueError("MAX_PDF_PAGES must be positive.")

        if self.CHUNK_SIZE <= 0:
            raise ValueError("CHUNK_SIZE must be positive.")

        if not 0 <= self.CHUNK_OVERLAP < self.CHUNK_SIZE:
            raise ValueError(
                "CHUNK_OVERLAP must be smaller than CHUNK_SIZE."
            )

        if self.HISTORY_TOKEN_BUDGET <= 0:
            raise ValueError(
                "HISTORY_TOKEN_BUDGET must be positive."
            )

        if self.RETRIEVER_TOP_K <= 0:
            raise ValueError("RETRIEVER_TOP_K must be positive.")


# --------------------------------------------------
# 5. CREATE SETTINGS OBJECT
# --------------------------------------------------

settings = Settings()

settings.validate_settings()
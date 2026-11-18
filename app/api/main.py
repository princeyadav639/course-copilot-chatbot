# main.py
import os
import tempfile
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.schemas.chat import ChatRequest
from app.schemas.document import (DocumentUploadResponse,DocumentDeleteResponse)
from app.services.chat_service import generate_chat_response
from app.services.document_service import (ingest_document,remove_document)
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# --------------------------------------------------
# 1. Application Configuration
# --------------------------------------------------

SESSION_SECRET = os.getenv("SESSION_SECRET")

if not SESSION_SECRET:
    raise RuntimeError(
        "SESSION_SECRET is missing. Add it to your .env file."
    )

app = FastAPI(
    title="Course Copilot API",
    description="API for Course Copilot Chatbot",
    version="1.0.0"
)

# Rate Limiter Configuration
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --------------------------------------------------
# 2. Session Middleware
# --------------------------------------------------

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="course_copilot_session",
    max_age=60 * 60 * 24 * 7,
    same_site="lax",
    https_only=(ENVIRONMENT == "production")
)


def get_session_id(request: Request) -> str:

    session_id = request.session.get("session_id")

    if not session_id:
        session_id = str(uuid4())
        request.session["session_id"] = session_id

    return session_id


# --------------------------------------------------
# 3. Health Check
# --------------------------------------------------

@app.get("/")
@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "application": settings.APP_NAME
    }


# --------------------------------------------------
# 4. Upload PDF
# --------------------------------------------------

@app.post("/upload",response_model=DocumentUploadResponse)
@limiter.limit("2/minute")
async def upload_pdf(request: Request,file: UploadFile = File(...)):

    session_id = get_session_id(request)

    filename = Path((file.filename or "").replace("\\", "/")).name

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.")

    if Path(filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.")

    document_id = str(uuid4())

    temp_path = None

    try:

        max_size = settings.MAX_PDF_SIZE_MB * 1024 * 1024

        total_size = 0

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp:

            temp_path = Path(temp.name)

            while True:

                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > max_size:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF exceeds the maximum allowed size."
                    )

                temp.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty."
            )

        # Check PDF file signature

        with temp_path.open("rb") as pdf_file:

            if pdf_file.read(5) != b"%PDF-":
                raise HTTPException(
                    status_code=400,
                    detail="Invalid PDF file."
                )

        # Process and store document chunks

        result = ingest_document(
            file_path=temp_path,
            original_filename=filename,
            document_id=document_id,
            session_id=session_id
        )

        return result

    except HTTPException:
        raise

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail="Document upload failed."
        ) from error

    finally:

        if temp_path and temp_path.exists():
            temp_path.unlink()

        await file.close()


# --------------------------------------------------
# 5. Delete PDF
# --------------------------------------------------

@app.delete("/documents/{document_id}",response_model=DocumentDeleteResponse)

def delete_pdf(document_id: str,request: Request):

    session_id = get_session_id(request)

    try:

        result = remove_document(
            session_id=session_id,
            document_id=document_id
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail="Document deletion failed."
        ) from error


# --------------------------------------------------
# 6. Chat Endpoint
# --------------------------------------------------

@app.post("/chat")
@limiter.limit("10/minute")
def receive_message(request: Request,payload: ChatRequest):

    print("DEBUG 1: Chat endpoint reached", flush=True)

    session_id = get_session_id(request)

    print("DEBUG 2: Session ID generated", flush=True)

    try:

        print("DEBUG 3: Calling chat service", flush=True)

        result = generate_chat_response(
            query=payload.message,
            session_id=session_id,
            history=payload.history
        )

        print("DEBUG 4: Chat service completed", flush=True)

        return {
            **result,
            "reply": result["answer"]
        }

    except ValueError as error:

        print(f"DEBUG ERROR: {error}", flush=True)

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        print(f"DEBUG ERROR: {error}", flush=True)

        raise HTTPException(
            status_code=500,
            detail="Unable to generate chatbot response."
        ) from error
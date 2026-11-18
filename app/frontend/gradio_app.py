# gradio_app.py
import os
import requests
import gradio as gr

from threading import Lock


# --------------------------------------------------
# 1. API Configuration
# --------------------------------------------------

# CHAT_URL = "http://127.0.0.1:8000/chat"
# UPLOAD_URL = "http://127.0.0.1:8000/upload"
API_BASE_URL = os.getenv("API_BASE_URL","http://127.0.0.1:8000").rstrip("/")
CHAT_URL = f"{API_BASE_URL}/chat"
UPLOAD_URL = f"{API_BASE_URL}/upload"
DELETE_URL = f"{API_BASE_URL}/documents"


REQUEST_TIMEOUT = 300
UPLOAD_TIMEOUT = 300


# --------------------------------------------------
# 2. User Session Management
# --------------------------------------------------

user_sessions = {}
user_documents = {}
session_lock = Lock()


def get_api_session(request: gr.Request):
    """
    Return a persistent requests.Session for each Gradio user.
    This preserves the FastAPI session cookie between requests.
    """

    session_id = request.session_hash

    with session_lock:

        if session_id not in user_sessions:
            user_sessions[session_id] = requests.Session()

        return user_sessions[session_id]


# --------------------------------------------------
# 3. PDF Upload
# --------------------------------------------------

def upload_pdf(file, api_session,session_id):
    """
    Upload a PDF to the FastAPI backend.
    """

    if isinstance(file, dict):
        path = file.get("path")
    else:
        path = file

    if not path or not os.path.isfile(path):
        return "Error: Uploaded file could not be found."

    try:

        with open(path, "rb") as pdf_file:

            response = api_session.post(
                UPLOAD_URL,
                files={
                    "file": (
                        os.path.basename(path),
                        pdf_file,
                        "application/pdf"
                    )
                },
                timeout=UPLOAD_TIMEOUT
            )

        response.raise_for_status()

        result = response.json()
        # Save document ID so it can be deleted later
        with session_lock:
            user_documents.setdefault(session_id, []).append(
                result["document_id"]
            )

        return (
            f"PDF uploaded successfully!\n"
            f"Filename: {result['filename']}\n"
            f"Document ID: {result['document_id']}\n"
            f"Total chunks: {result['total_chunks']}"
        )

    except requests.exceptions.ConnectionError:

        return "Error: FastAPI server is not running."

    except requests.exceptions.Timeout:

        return "Error: PDF upload timed out. Please try again."

    except requests.exceptions.HTTPError as error:

        return f"Upload failed: {error.response.text}"

    except (KeyError, ValueError):

        return "Error: Unexpected response received from the API."

    except requests.exceptions.RequestException as error:

        return f"Upload Error: {error}"


# --------------------------------------------------
# 4. Chat Request
# --------------------------------------------------

def ask_bot(text, history, api_session):
    """
    Send the user's message and conversation history
    to the FastAPI backend.
    """

    try:

        response = api_session.post(
            CHAT_URL,
            json={
                "message": text,
                "history": history
            },
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        result = response.json()

        answer = result.get("answer", result.get("reply", ""))

        if isinstance(answer, str):
            return answer

        if isinstance(answer, list):
            parts = []

            for item in answer:
                if isinstance(item, str):
                    parts.append(item)

                elif isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        parts.append(text)

                else:
                    text = getattr(item, "text", None)
                    if isinstance(text, str):
                        parts.append(text)
            return "\n".join(parts) or "No readable response received."

        return str(answer)


    except requests.exceptions.ConnectionError:

        return "Error: FastAPI server is not running."

    except requests.exceptions.Timeout:

        return "Error: The chatbot took too long to respond."

    except requests.exceptions.HTTPError as error:

        return f"API Error: {error.response.text}"

    except (KeyError, ValueError):

        return "Error: Unexpected response received from the API."

    except requests.exceptions.RequestException as error:

        return f"API Error: {error}"


# --------------------------------------------------
# 5. Main Chat Function
# --------------------------------------------------

def chat_with_bot(message, history, request: gr.Request):

    api_session = get_api_session(request)
    session_id = request.session_hash

    text = message.get("text", "").strip()
    files = message.get("files", [])

    if not isinstance(files, list):
        files = [files] if files else []

    replies = []

    # Upload attached PDFs first.

    for file in files:

        upload_result = upload_pdf(
            file=file,
            api_session=api_session,
            session_id=session_id
        )

        replies.append(upload_result)

        # Stop if an upload fails.
        if not upload_result.startswith("PDF uploaded successfully!"):

            return "\n\n".join(replies)

    # Send the user's question to the chatbot.

    if text:

        answer = ask_bot(
            text=text,
            history=history,
            api_session=api_session
        )

        replies.append(answer)

    elif not files:

        return "Please enter a message or upload a PDF."

    return "\n\n".join(replies)

# --------------------------------
# 6. Clear Chat + Delete PDFs
# --------------------------------

def clear_chat_and_delete_pdfs(request: gr.Request):

    session_id = request.session_hash

    api_session = get_api_session(request)

    with session_lock:

        document_ids = list(
            user_documents.get(session_id, [])
        )

    remaining_documents = []

    for document_id in document_ids:

        try:

            response = api_session.delete(
                f"{DELETE_URL}/{document_id}",
                timeout=30
            )

            response.raise_for_status()

            print(f"Deleted document: {document_id}")

        except requests.exceptions.RequestException as error:

            print(
                f"Could not delete document {document_id}: {error}"
            )

            remaining_documents.append(document_id)

    # Keep only documents that could not be deleted

    with session_lock:

        user_documents[session_id] = remaining_documents

    print("Chat cleared. PDF deletion process completed.")

# --------------------------------------------------
# 6. Gradio Interface
# --------------------------------------------------
with gr.Blocks() as demo:
    chatbot = gr.Chatbot()

    chatbot.clear(
    fn=clear_chat_and_delete_pdfs,
    inputs=None,
    outputs=None)

    gr.ChatInterface(
        fn=chat_with_bot,chatbot=chatbot,

        multimodal=True,

        textbox=gr.MultimodalTextbox(
            file_types=[".pdf"],
            file_count="multiple",
            placeholder="Ask a question or upload PDF documents..."
        ),

        title="Course Copilot",

        description=(
            "Your AI-powered learning assistant. "
            "Upload PDFs and ask questions about your documents."
        )
    )


# --------------------------------------------------
# 7. Launch Application
# --------------------------------------------------

if __name__ == "__main__":

    demo.launch()
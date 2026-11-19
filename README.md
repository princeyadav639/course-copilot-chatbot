# Course Copilot 🎓

Course Copilot is an AI-powered learning assistant that helps students learn from their study materials. Upload PDF documents, ask questions, and get relevant answers through an interactive chatbot.

It also provides additional learning resources through web search, Wikipedia, and YouTube.

## Features

- **PDF Question Answering:** Upload PDFs and ask questions about their content.
- **RAG-Based Responses:** Generates contextual answers using relevant information from uploaded documents.
- **Multiple PDF Uploads:** Upload and manage multiple documents.
- **Chat History:** Maintains conversation context.
- **Web Search:** Find additional information from the internet.
- **Wikipedia & YouTube:** Access useful information and educational videos.
- **Session Isolation:** Keeps users' uploaded documents separate.
- **Document Management:** Delete uploaded documents and their associated vector data.

## Tech Stack

- Python
- FastAPI
- Gradio
- LangChain
- Groq LLM
- Google Gemini Embeddings
- ChromaDB
- Docker & Docker Compose

## How to Run

### Option 1: Using Docker (Recommended)

**Step 1: Clone the repository**

```bash
git clone https://github.com/princeyadav639/course-copilot-chatbot.git
cd course-copilot-chatbot
```

**Step 2: Configure environment variables**

Create a `.env` file:

```powershell
Copy-Item .env.example .env
```

Add your required API keys and configuration values to the `.env` file.

**Step 3: Build and start the application**

```bash
docker compose up --build -d
```

**Step 4: Open the chatbot**

http://localhost:7860

### Option 2: Run Locally

**Step 1: Clone the repository**

```bash
git clone https://github.com/princeyadav639/course-copilot-chatbot.git
cd course-copilot-chatbot
```

**Step 2: Create a virtual environment**

```bash
python -m venv myenv
```

Activate it:

```powershell
.\myenv\Scripts\Activate
```

**Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 4: Configure environment variables**

```powershell
Copy-Item .env.example .env
```

Add your required API keys and configuration values.

**Step 5: Start the FastAPI backend**

Open the first terminal:

```bash
uvicorn app.api.main:app --reload --port 8000
```

**Step 6: Start the Gradio frontend**

Open a second terminal:

```bash
python -c "from app.frontend.gradio_app import demo; demo.launch(server_name='127.0.0.1', server_port=7860)"
```

**Step 7: Open the chatbot**

http://localhost:7860

## How to Use

1. Open Course Copilot in your browser.
2. Upload one or more PDF documents.
3. Ask questions about your uploaded documents.
4. Get AI-generated answers based on the available context.
5. Use web search, Wikipedia, or YouTube for additional information.
6. Delete uploaded documents when they are no longer needed.

## Made By

**Prince Yadav**

BS-MS (Mathematics and Data Science)
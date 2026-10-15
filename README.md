# AutoAssist AI — Car Buying & Ownership Assistant

A small portfolio project that demonstrates an LLM-powered chatbot with a Flask backend, OpenAI API integration, short-term conversation memory, and a local knowledge base for car buying and ownership questions.

> Independent learning project. Not affiliated with CARS24 or any car retailer. AI answers may be inaccurate and should be verified.

## Features

- Chat UI built with HTML, CSS, and vanilla JavaScript
- Flask API endpoint for chat requests
- OpenAI Chat Completions API integration
- Short conversation history stored in the Flask session
- Lightweight keyword-overlap retrieval from a local car knowledge base
- Retrieved notes included as context for the LLM
- Example prompts, new-chat reset, and basic input validation
- API key loaded from environment variables; no secret is committed

## Tech stack

Python · Flask · OpenAI API · HTML · CSS · JavaScript · Git

## Run locally

### 1. Requirements
- Python 3.10 or newer
- An OpenAI API key with API access and billing configured

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env`, then replace the placeholder values:

Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

macOS/Linux:
```bash
cp .env.example .env
```

Edit `.env` and add your own API key. **Never commit `.env` or paste your API key into source code.** The `.gitignore` already excludes `.env`.

### 5. Start the app

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## How it works

1. The browser sends the user's message to `POST /api/chat`.
2. The Flask app finds relevant local notes using basic keyword overlap.
3. The app sends the system instructions, retrieved notes, recent conversation turns, and current message to the OpenAI API.
4. The assistant response and a short conversation history are returned to the browser.
5. `POST /api/reset` clears the session conversation history.

## Current limitations

- Retrieval is keyword-based, not semantic vector search. It is a small RAG-style prototype, not a production retrieval system.
- The local knowledge base is illustrative and limited; it is not live vehicle, inventory, pricing, or legal data.
- There is no authentication, persistent database, rate limiting, or production deployment configuration.
- The default Flask development server is for local testing only.
- API usage may incur charges depending on your OpenAI account.

## Ideas for next improvements

- Add automated tests for retrieval and API error handling.
- Replace keyword overlap with embeddings and a vector store.
- Add a persistent database for user-approved conversation history.
- Add rate limiting and stronger session-secret handling.
- Deploy with a production WSGI server and configure secrets through the hosting platform.

## Suggested GitHub description

`LLM-powered car buying assistant built with Flask, OpenAI API, conversation memory, and lightweight local knowledge retrieval.`

## Resume bullet (use only after you run and test it)

**AutoAssist AI — Car Buying & Ownership Assistant** | Python, Flask, OpenAI API, JavaScript  
- Built a web chatbot integrating an LLM API, prompt instructions, and short-term conversation memory.
- Implemented keyword-based retrieval over a local car knowledge base to supply contextual notes to the model.
- Added a responsive chat interface, input validation, session reset, and environment-based secret management.

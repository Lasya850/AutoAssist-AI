import os
import re
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-development-secret")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Small, local knowledge base for the demo. This is keyword-based retrieval,
# not a production-grade semantic search system.
KNOWLEDGE_BASE = [
    {
        "title": "Used-car inspection checklist",
        "content": "Before buying a used car, inspect service records, ownership history, odometer consistency, accident or flood damage, tyres, brakes, lights, AC, battery, engine noise, leaks, and warning lights. Take a test drive and arrange an independent mechanic inspection. Verify the VIN and documents."
    },
    {
        "title": "Documents to verify",
        "content": "For a used-car purchase in India, verify the Registration Certificate (RC), seller identity, valid insurance, PUC certificate where applicable, loan hypothecation status, service records, and any pending challans. Follow the relevant state transport department process for ownership transfer."
    },
    {
        "title": "Test-drive tips",
        "content": "During a test drive, check cold start behaviour, steering alignment, braking, clutch and gear changes, suspension sounds, AC performance, dashboard warning lights, reverse gear, and behaviour at low and highway speeds where safe and legal."
    },
    {
        "title": "Maintenance basics",
        "content": "Follow the manufacturer's service schedule. Check tyre pressure and tread, engine oil, coolant, brake fluid, battery condition, lights, wipers, and warning indicators. Use the owner's manual for vehicle-specific intervals and specifications."
    },
    {
        "title": "Budgeting for ownership",
        "content": "Estimate total ownership cost, not just purchase price. Include insurance, fuel or charging, scheduled maintenance, tyres, repairs, parking, taxes, and financing costs. Keep a contingency for unexpected repairs and compare quotes before committing."
    },
    {
        "title": "Electric vehicle basics",
        "content": "When evaluating an electric vehicle, consider real-world range, battery warranty and health report, charging access at home and work, public charging availability, charging speed, service support, and the cost of replacing out-of-warranty components."
    }
]

SYSTEM_PROMPT = """You are AutoAssist, a helpful assistant for people researching car buying and ownership.
Give practical, clear answers. Use the provided reference notes when relevant, but do not pretend they cover every vehicle or legal situation.
Do not invent vehicle-specific specifications, prices, warranty terms, or legal requirements. Say when details depend on the model, state, or current policy.
For safety-critical repairs, advise the user to consult a qualified mechanic. You are not affiliated with CARS24 or any car retailer.
Keep answers concise and use bullets when useful."""

def retrieve_context(question, limit=3):
    """Simple token-overlap retrieval from the local knowledge base."""
    tokens = set(re.findall(r"[a-z0-9]+", question.lower()))
    stop_words = {"the", "and", "for", "with", "how", "what", "are", "is", "to", "a", "an", "in", "of", "my", "i", "do", "can", "should"}
    tokens -= stop_words
    scored = []
    for item in KNOWLEDGE_BASE:
        text_tokens = set(re.findall(r"[a-z0-9]+", (item["title"] + " " + item["content"]).lower()))
        score = len(tokens & text_tokens)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:limit]]

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Please enter a message."}), 400
    if len(message) > 2000:
        return jsonify({"error": "Please keep messages under 2,000 characters."}), 400
    if not API_KEY:
        return jsonify({
            "error": "OPENAI_API_KEY is not configured. Copy .env.example to .env and add your API key."
        }), 503

    try:
        client = OpenAI(api_key=API_KEY)
        history = session.get("history", [])
        references = retrieve_context(message)
        reference_text = "\n\n".join(
            f"{item['title']}: {item['content']}" for item in references
        ) or "No directly matching local reference notes were found."

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.append({
            "role": "system",
            "content": "Local reference notes (use only when relevant):\n" + reference_text
        })
        # Keep a short recent conversation to provide conversational context.
        messages.extend(history[-8:])
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.4,
            max_tokens=500
        )
        answer = response.choices[0].message.content or "Sorry, I couldn't generate a response."
        history = (history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer}
        ])[-10:]
        session["history"] = history

        return jsonify({
            "answer": answer,
            "sources": [item["title"] for item in references],
            "model": MODEL
        })
    except Exception as exc:
        # Keep technical details out of the browser response.
        app.logger.exception("Chat request failed")
        return jsonify({
            "error": "The AI request failed. Check your API key, model access, and internet connection, then try again."
        }), 502

@app.post("/api/reset")
def reset_chat():
    session.pop("history", None)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)

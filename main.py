from boltiotai import openai
import os
from flask import Flask, render_template_string, request, session, jsonify, redirect, url_for

# ========================
# OpenAI / BoltIOT config
# ========================
openai.api_key = os.environ.get('OPENAI_API_KEY', '')

# ========================
# Flask app config
# ========================
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

SYSTEM_PROMPT = (
    "You are a helpful and expert travel planner AI. "
    "When a user provides a destination, number of days, and preferences, generate a detailed, day-wise itinerary. "
    "Include attractions, local experiences, and food suggestions. Keep it concise but informative. "
    "Format each day's plan clearly. "
    "If needed, ask follow-up questions about budget or interests."
)

def call_model(messages):
    response = openai.chat.completions.create(
        model="gpt-3.5",
        messages=messages,
    )
    return response["choices"][0]["message"]["content"].strip()

def get_history():
    history = session.get("history")
    if not history:
        history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        session["history"] = history
    return history

def add_to_history(role, content):
    history = get_history()
    history.append({"role": role, "content": content})
    session["history"] = history

@app.route("/", methods=["GET"])
def home():
    history = get_history()
    display_history = [m for m in history if m["role"] != "system"]
    return render_template_string(TEMPLATE, history=display_history)

@app.route("/ask", methods=["POST"])
def ask():
    destination = request.form.get("destination", "").strip()
    days = request.form.get("days", "").strip()
    preferences = request.form.get("preferences", "").strip()

    if not destination or not days.isdigit():
        return jsonify({"error": "Please enter a valid destination and number of days."}), 400

    user_msg = (
        f"Plan a {days}-day trip to {destination}. "
        f"My preferences: {preferences if preferences else 'general tourist experience'}."
    )
    add_to_history("user", user_msg)

    history = get_history()
    try:
        answer = call_model(history)
    except Exception as e:
        return jsonify({"error": f"Model/API error: {e}"}), 500

    add_to_history("assistant", answer)
    return jsonify({"answer": answer})

@app.route("/clear", methods=["POST"])
def clear():
    session.pop("history", None)
    return redirect(url_for("home"))

TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Travel Itinerary Generator</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet" />
  <style>
    :root {
      --bg: #eef2ff;
      --bg-accent-1: #c7d2fe;
      --bg-accent-2: #e0e7ff;
      --card-bg: rgba(255, 255, 255, 0.6);
      --border: rgba(255, 255, 255, 0.35);
      --text: #0f172a;
      --muted: #475569;
      --user-bubble: #cfe1ff;
      --assistant-bubble: #f1f3f5;
    }
    html, body {
      height: 100%;
      font-family: 'Segoe UI', sans-serif;
      color: var(--text);
      background: radial-gradient(circle at 10% 20%, var(--bg) 0%, var(--bg-accent-2) 50%, var(--bg-accent-1) 100%);
    }
    .glass-card {
      background: var(--card-bg);
      backdrop-filter: blur(14px) saturate(160%);
      -webkit-backdrop-filter: blur(14px) saturate(160%);
      border: 1px solid var(--border);
      border-radius: 16px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.06);
      padding: 1rem;
    }
    .chat-window {
      height: 60vh;
      overflow-y: auto;
    }
    .message { margin-bottom: 1rem; }
    .message pre { white-space: pre-wrap; margin: 0; }
    .message .role { font-size: 0.85rem; color: var(--muted); }
    .message .bubble {
      display: inline-block;
      padding: 0.75rem 1rem;
      border-radius: 12px;
      margin: 0.25rem 0;
      max-width: 100%;
      white-space: pre-wrap;
    }
    .message.user { text-align: right; }
    .message.user .bubble { background: var(--user-bubble); }
    .message.assistant .bubble { background: var(--assistant-bubble); text-align: left; }
  </style>
</head>
<body>
  <div class="container py-4">
    <h1 class="mb-4 text-primary">🌍 Travel Itinerary Generator</h1>
    <form action="/clear" method="POST" class="mb-3">
      <button type="submit" class="btn btn-outline-danger btn-sm">Clear Conversation</button>
    </form>
    <div class="glass-card chat-window mb-3" id="chat-window">
      {% for msg in history %}
        <div class="message {{ msg.role }}">
          <div class="role">{{ msg.role|capitalize }}</div>
          <div class="bubble"><pre>{{ msg.content }}</pre></div>
        </div>
      {% endfor %}
    </div>
    <form id="ask-form" class="glass-card" onsubmit="event.preventDefault(); askItinerary();">
      <div class="row g-2 mb-2">
        <div class="col-md-4">
          <label for="destination" class="form-label">Destination</label>
          <input type="text" id="destination" name="destination" class="form-control" required />
        </div>
        <div class="col-md-2">
          <label for="days" class="form-label">No. of Days</label>
          <input type="number" id="days" name="days" class="form-control" min="1" required />
        </div>
        <div class="col-md-6">
          <label for="preferences" class="form-label">Travel Preferences (optional)</label>
          <input type="text" id="preferences" name="preferences" class="form-control" placeholder="e.g., beaches, culture, food" />
        </div>
      </div>
      <div class="d-flex justify-content-end">
        <button type="submit" class="btn btn-primary">Generate Itinerary</button>
      </div>
    </form>
  </div>
  <script>
    async function askItinerary() {
      const destination = document.getElementById('destination').value.trim();
      const days = document.getElementById('days').value.trim();
      const preferences = document.getElementById('preferences').value.trim();
      if (!destination || !days) return;

      const chatWindow = document.getElementById('chat-window');
      const userBlock = document.createElement('div');
      userBlock.className = 'message user';
      userBlock.innerHTML = `<div class="role">User</div><div class="bubble"><pre>${escapeHtml(destination + " - " + days + " days\n" + preferences)}</pre></div>`;
      chatWindow.appendChild(userBlock);
      chatWindow.scrollTop = chatWindow.scrollHeight;

      const typing = document.createElement('div');
      typing.className = 'message assistant';
      typing.innerHTML = '<div class="role">Assistant</div><div class="bubble">Planning your trip…</div>';
      chatWindow.appendChild(typing);
      chatWindow.scrollTop = chatWindow.scrollHeight;

      try {
        const formData = new FormData();
        formData.append('destination', destination);
        formData.append('days', days);
        formData.append('preferences', preferences);

        const response = await fetch('/ask', {
          method: 'POST',
          body: formData
        });

        const data = await response.json();
        typing.querySelector('.bubble').innerHTML = '<pre>' + escapeHtml(data.answer || 'No itinerary generated.') + '</pre>';
      } catch (err) {
        typing.querySelector('.bubble').innerText = 'Network error. Please try again.';
      } finally {
        document.getElementById('preferences').value = '';
        chatWindow.scrollTop = chatWindow.scrollHeight;
      }
    }

    function escapeHtml(string) {
      const div = document.createElement('div');
      div.appendChild(document.createTextNode(string));
      return div.innerHTML;
    }
  </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

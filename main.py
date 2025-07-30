from openai import OpenAI
import os
from flask import Flask, render_template_string, request, session, jsonify, redirect, url_for

# ========================
# OpenAI config
# ========================
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', ''))

# ========================
# Flask app config
# ========================
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

SYSTEM_PROMPT = (
    "You are an expert programming assistant. "
    "Your task is to analyze code snippets given by users, detect errors (if any), "
    "explain what the issue is, and provide corrected versions of the code. "
    "Only answer code-related questions. If the input is not code, politely refuse."
)

def call_model(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    choices = response.choices
    if not choices or not choices[0].message.content.strip():
        return "Sorry, I couldn't process the code. Please try again with a valid snippet."
    return choices[0].message.content.strip()

def get_history():
    history = session.get("history")
    if not history:
        history = [{"role": "system", "content": SYSTEM_PROMPT}]
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
    code = request.form.get("code", "").strip()
    if not code:
        return jsonify({"error": "Please enter some code."}), 400

    add_to_history("user", code)
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
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Code Error Detector</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: linear-gradient(to right, #141e30, #243b55);
      color: white;
      font-family: 'Segoe UI', sans-serif;
    }
    .glass-card {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      border-radius: 15px;
      padding: 20px;
      margin-bottom: 20px;
      border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .message {
      margin-bottom: 1rem;
    }
    .message .role {
      font-weight: bold;
    }
    .user .bubble {
      background: #0d6efd;
      color: white;
      border-radius: 8px;
      padding: 10px;
    }
    .assistant .bubble {
      background: #343a40;
      color: white;
      border-radius: 8px;
      padding: 10px;
    }
    pre {
      white-space: pre-wrap;
      word-wrap: break-word;
    }
  </style>
</head>
<body>
<div class="container py-5">
  <h1 class="mb-4 text-info">💡 AI Code Error Detector & Corrector</h1>
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
  <form id="ask-form" class="glass-card" onsubmit="event.preventDefault(); askCodeFix();">
    <div class="mb-3">
      <label for="code" class="form-label">Paste your code here</label>
      <textarea id="code" name="code" class="form-control" rows="6" required placeholder="e.g. def hello(:\n  print('Hi')"></textarea>
    </div>
    <div class="d-flex justify-content-end">
      <button type="submit" class="btn btn-primary">Check Code</button>
    </div>
  </form>
</div>
<script>
  async function askCodeFix() {
    const code = document.getElementById('code').value.trim();
    if (!code) return;

    const chatWindow = document.getElementById('chat-window');
    const userBlock = document.createElement('div');
    userBlock.className = 'message user';
    userBlock.innerHTML = `<div class="role">User</div><div class="bubble"><pre>${escapeHtml(code)}</pre></div>`;
    chatWindow.appendChild(userBlock);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    const typing = document.createElement('div');
    typing.className = 'message assistant';
    typing.innerHTML = '<div class="role">Assistant</div><div class="bubble">Analyzing your code…</div>';
    chatWindow.appendChild(typing);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
      const formData = new FormData();
      formData.append('code', code);

      const response = await fetch('/ask', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      typing.querySelector('.bubble').innerHTML = '<pre>' + escapeHtml(data.answer || 'No response.') + '</pre>';
    } catch (err) {
      typing.querySelector('.bubble').innerText = 'Network error. Please try again.';
    } finally {
      document.getElementById('code').value = '';
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

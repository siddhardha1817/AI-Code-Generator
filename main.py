from boltiotai import openai
import os
from flask import Flask, render_template_string, request, session, jsonify, redirect, url_for

# ========================
# OpenAI / BoltIOT config
# ========================
open_api_key = os.environ.get('OPEN_API_KEY', '')

# ========================
# Flask app config
# ========================
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

# Prompt focused on code generation
SYSTEM_PROMPT = (
    "You are a Code Snippet Generator. "
    "Given a programming task or description, generate clean and efficient code for it. "
    "Respond with a code block only. Do not include explanations unless asked. "
    "Support Python, JavaScript, C++, Java, and other major languages. "
    "If the user does not mention a language, assume Python."
)

def call_model(messages):
    """Call the language model with chat history."""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        api_key=open_api_key  # ← Using open_api_key here
    )
    return response["choices"][0]["message"]["content"].strip()

def get_history():
    """Initialize or return chat history."""
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
    question = request.form.get("question", "").strip()
    if not question:
        return jsonify({"error": "Please enter a valid prompt."}), 400

    add_to_history("user", question)

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

# Template included below
TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Code Snippet Generator</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet" />
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background: #eef2ff;
      color: #0f172a;
    }
    .chat-window {
      height: 60vh;
      overflow-y: auto;
      background: #fff;
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 1rem;
    }
    .message { margin-bottom: 1rem; }
    .message pre { white-space: pre-wrap; margin: 0; }
    .message .role { font-size: 0.85rem; color: #555; }
    .message.user .bubble { background: #cfe1ff; padding: 0.75rem; border-radius: 10px; }
    .message.assistant .bubble { background: #f1f3f5; padding: 0.75rem; border-radius: 10px; }
  </style>
</head>
<body>
  <div class="container py-4">
    <h1 class="mb-4 text-primary">💻 Code Snippet Generator</h1>
    <form action="/clear" method="POST" class="mb-3">
      <button type="submit" class="btn btn-outline-danger btn-sm">Clear Chat</button>
    </form>
    <div class="chat-window" id="chat-window">
      {% for msg in history %}
        <div class="message {{ msg.role }}">
          <div class="role">{{ msg.role|capitalize }}</div>
          <div class="bubble"><pre>{{ msg.content }}</pre></div>
        </div>
      {% endfor %}
    </div>
    <form id="ask-form" onsubmit="event.preventDefault(); askPrompt();">
      <div class="mb-3">
        <label for="question" class="form-label">Describe your task or code prompt:</label>
        <textarea id="question" name="question" class="form-control" rows="3" placeholder="E.g., Create a Python function to check for prime numbers" required></textarea>
      </div>
      <div class="d-flex justify-content-end">
        <button type="submit" class="btn btn-success">Generate Code</button>
      </div>
    </form>
  </div>

  <script>
    async function askPrompt() {
      const question = document.getElementById('question').value.trim();
      if (!question) return;

      const chatWindow = document.getElementById('chat-window');
      const userBlock = document.createElement('div');
      userBlock.className = 'message user';
      userBlock.innerHTML = <div class="role">User</div><div class="bubble"><pre>${escapeHtml(question)}</pre></div>;
      chatWindow.appendChild(userBlock);
      chatWindow.scrollTop = chatWindow.scrollHeight;

      const typing = document.createElement('div');
      typing.className = 'message assistant';
      typing.innerHTML = '<div class="role">Assistant</div><div class="bubble">Generating snippet...</div>';
      chatWindow.appendChild(typing);
      chatWindow.scrollTop = chatWindow.scrollHeight;

      try {
        const formData = new FormData();
        formData.append('question', question);

        const response = await fetch('/ask', {
          method: 'POST',
          body: formData
        });

        const data = await response.json();
        if (!response.ok) {
          typing.querySelector('.bubble').innerText = data.error || 'Something went wrong.';
        } else {
          typing.querySelector('.bubble').innerHTML = '<pre>' + escapeHtml(data.answer) + '</pre>';
        }
      } catch (err) {
        typing.querySelector('.bubble').innerText = 'Network error. Please try again.';
      } finally {
        document.getElementById('question').value = '';
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
# AI Code Generator with Step-by-Step Explanation

An AI-powered Flask web application that generates programming solutions along with detailed algorithmic explanations using OpenAI/BoltIOT APIs.

---

# Features

- AI-based code generation
- Step-by-step algorithm explanation
- Interactive chat interface
- Session-based conversation history
- Clean Bootstrap UI
- Flask backend integration
- Real-time response generation
- Clear chat functionality

---

# Tech Stack

## Frontend
- HTML
- CSS
- JavaScript
- Bootstrap 5

## Backend
- Python
- Flask

## AI Integration
- OpenAI API
- BoltIOT AI SDK

---

# Project Structure

```bash
project-folder/
│
├── main.py
├── requirements.txt
├── README.md
└── .replit
```

---

# Installation

## Clone the Repository

```bash
git clone https://github.com/siddhardha1817/AI-Code-Generator.git
```

## Move into Project Directory

```bash
cd AI-Code-Generator.git
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# requirements.txt

```txt
Flask
openai
boltiotai
gunicorn
python-dotenv
```

---

# Environment Variables

Add the following secrets in Replit or create a `.env` file.

```env
OPEN_API_KEY=your_openai_api_key
FLASK_SECRET_KEY=your_secret_key
```

---

# Run the Application

```bash
python main.py
```

The application will run on:

```text
http://0.0.0.0:8080
```

---

# How It Works

1. User enters a programming prompt.
2. Flask sends the prompt to the OpenAI model.
3. The AI generates:
   - Step-by-step explanation
   - Fully working code
4. Response is displayed in the chat interface.

---

# Example Prompt

```text
Write a Python program to check whether a number is prime
```

---

# Screenshots

Add screenshots of:
- Home Page
- Chat Interface
- Generated Code Output
- Step-by-Step Explanation

---

# Future Improvements

- Syntax highlighting
- Multiple programming language support
- User authentication
- Database integration
- Download generated code
- Dark mode support
- Voice prompt support

---

# Deployment

You can deploy this project using:

- Replit
- Render
- Railway
- Heroku

---

# Live Demo

https://84c409a6-3f7d-4fd9-976d-6dc05ef41c9b-00-1lcjfv8w117hy.pike.replit.dev/

# GitHub Repository

```text
https://github.com/siddhardha1817/AI-Code-Generator/
```

---

# Author

Siddhardha Mangi

GitHub:
https://github.com/siddhardha1817

---

# License

This project is developed for educational and learning purposes.

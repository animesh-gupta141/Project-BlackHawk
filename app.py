from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import sqlite3

DB_FILE = "chats.db"
load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_FILE = "chats.json"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

def load_chats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT data FROM chats ORDER BY id DESC LIMIT 1")
    row = c.fetchone()

    conn.close()

    if row:
        return json.loads(row[0])

    return []

def save_chats(chats):

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("DELETE FROM chats")

    c.execute(
        "INSERT INTO chats (data) VALUES (?)",
        (json.dumps(chats),)
    )

    conn.commit()
    conn.close()

@app.route("/health")
def health():
    return "OK"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/load_chats")
def load():
    return jsonify(load_chats())


@app.route("/save_chats", methods=["POST"])
def save():
    chats = request.json
    save_chats(chats)
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    messages = data["messages"]
    model = data.get("model", "gpt-4.1-mini")

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )

    reply = ""

    for chunk in stream:
        if chunk.choices[0].delta.content:
            reply += chunk.choices[0].delta.content

    return jsonify({"reply": reply})
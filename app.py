from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_FILE = "chats.json"


def load_chats():
    if not os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "w") as f:
            json.dump([], f)
        return []

    with open(CHAT_FILE, "r") as f:
        return json.load(f)


def save_chats(chats):
    with open(CHAT_FILE, "w") as f:
        json.dump(chats, f)


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
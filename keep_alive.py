# keep_alive.py (Render 환경 유지용)
from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "BTC Trading Bot is alive"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

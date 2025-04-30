from flask import Flask
from threading import Thread
import os

app = Flask('keep_alive')

@app.route('/')
def home():
    return "✅ BTC Trading Bot is alive and running!"

def run():
    port = int(os.environ.get("PORT", 10001))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()


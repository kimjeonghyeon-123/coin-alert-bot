from flask import Flask
from threading import Thread
import os
import subprocess
import signal

app = Flask('keep_alive')

@app.route('/')
def home():
    return "✅ BTC Trading Bot is alive and running!"

def release_port(port):
    """포트 점유 상태를 확인하고, 점유된 프로세스를 종료하는 함수"""
    try:
        process = subprocess.Popen(f"lsof -ti :{port}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if out:
            pid = int(out.decode().strip())  # PID를 정수로 변환
            # 해당 프로세스를 강제 종료
            os.kill(pid, signal.SIGKILL)
            print(f"Port {port} is being used. Process {pid} has been killed.")
        else:
            print(f"Port {port} is free.")
    except Exception as e:
        print(f"Error while releasing port {port}: {e}")

def run():
    """Flask 앱을 실행하는 함수"""
    port = int(os.environ.get("PORT", 10001))

    # 포트 점유 상태를 확인하고 해제
    release_port(port)

    # Flask 앱을 실행
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    """Flask 앱을 백그라운드에서 실행하는 함수"""
    t = Thread(target=run)
    t.daemon = True
    t.start()

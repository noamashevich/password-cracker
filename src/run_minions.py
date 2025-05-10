import subprocess
import sys
import os
import time
import threading
from config_loader import load_config

CONFIG = load_config()

NUM_MINIONS = CONFIG["num_minions"]
START_PORT = CONFIG["start_port"]

SCRIPT_NAME = "minion.py"

def run_minion(port):
    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"

    return subprocess.Popen(
        [sys.executable, SCRIPT_NAME, "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # מאחד stdout ו-stderr
        text=True,
        env=env
    )

def stream_output(port, proc):
    for line in proc.stdout:
        if line:
            print(f"[Minion {port}] {line.strip()}")

if __name__ == "__main__":
    processes = []

    print("Launching minions...")
    print(NUM_MINIONS)
    for i in range(NUM_MINIONS):
        port = START_PORT + i
        print(f"Launching Minion on port {port}...")
        proc = run_minion(port)
        thread = threading.Thread(target=stream_output, args=(port, proc), daemon=True)
        thread.start()
        processes.append((port, proc))

    print("All minions launched. Listening for output.\nPress Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping all minions...")
        for _, proc in processes:
            proc.terminate()

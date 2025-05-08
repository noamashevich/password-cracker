import subprocess
import time
import threading
import os
import sys

NUM_MINIONS = 4
BASE_PORT = 5001
processes = []

#  נתיב לפייתון מתוך ה־venv
PYTHON_EXECUTABLE = os.path.join(".", ".venv", "Scripts", "python.exe")
if not os.path.exists(PYTHON_EXECUTABLE):
    print("Flask not found — make sure you have a .venv and Flask installed.")
    sys.exit(1)


def stream_output(port, proc):
    for line in proc.stdout:
        print(f"[Minion {port}] {line.decode().strip()}")


for i in range(NUM_MINIONS):
    port = BASE_PORT + i
    print(f"Launching Minion on port {port}")

    proc = subprocess.Popen(
        [PYTHON_EXECUTABLE, "minion.py", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    threading.Thread(target=stream_output, args=(port, proc), daemon=True).start()
    processes.append((port, proc))
    time.sleep(0.3)

print("All minions launched. Press Ctrl+C to stop them.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping all minions...")
    for port, proc in processes:
        proc.terminate()
        print(f"Minion on port {port} terminated.")

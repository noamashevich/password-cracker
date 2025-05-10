import subprocess
import sys
import os
import time
import threading
from config_loader import load_config

CONFIG = load_config()

NUM_MINIONS = CONFIG["num_minions"]
START_PORT = CONFIG["start_port"]
SCRIPT_NAME = "src/minion.py"

def run_minion(port):
    """
    Starts a minion process on the specified port.
    Returns the subprocess.Popen object.
    """
    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"

    return subprocess.Popen(
        [sys.executable, SCRIPT_NAME, "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )

def stream_output(port, proc, restart_callback):
    """
    Streams output from a minion process.
    If the process ends unexpectedly, calls the restart callback.
    """
    try:
        for line in proc.stdout:
            if line:
                print(f"[Minion {port}] {line.strip()}")
    except Exception as e:
        print(f"[Minion {port}] Error reading output: {e}")
    finally:
        if proc.poll() is not None:  # If process ended
            print(f"[Minion {port}] Process ended. Restarting...")
            restart_callback(port)

def launch_and_monitor(port):
    """
    Launches a minion and starts monitoring its output.
    If it crashes, it will be restarted.
    """
    proc = run_minion(port)

    def restart(port_to_restart):
        time.sleep(1)
        launch_and_monitor(port_to_restart)

    thread = threading.Thread(target=stream_output, args=(port, proc, restart), daemon=True)
    thread.start()
    return proc

if __name__ == "__main__":
    processes = []

    print("Launching minions...")
    for i in range(NUM_MINIONS):
        port = START_PORT + i
        print(f"Launching Minion on port {port}...")
        proc = launch_and_monitor(port)
        processes.append((port, proc))

    print("All minions launched. Listening for output.\nPress Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping all minions...")
        for _, proc in processes:
            proc.terminate()

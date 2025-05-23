import subprocess
import sys
import os
import time
import threading
from config_loader import load_config

# Load configuration from config.json
CONFIG = load_config()

NUM_MINIONS = CONFIG["num_minions"]
START_PORT = CONFIG["start_port"]
SCRIPT_NAME = "src/minion.py"

def run_minion(port: int):
    """
    Starts a minion process on the specified port.
    Returns the subprocess.Popen object.
    :param port: The specified port
    :return: The subprocess.Popen object
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

def stream_output(port: int, proc, restart_callback):
    """
    Streams output from a minion process.
    If the process ends unexpectedly, calls the restart callback.
    :param port: The specified port
    :param proc: The subprocess.Popen object
    :param restart_callback: The retry function
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

def launch_and_monitor(port: int):
    """
    Launches a minion and starts monitoring its output.
    If it crashes, it will be restarted.
    :param port: The minion port
    :return: The process object
    """
    proc = run_minion(port)

    def restart(port_to_restart):
        time.sleep(1)
        launch_and_monitor(port_to_restart)

    thread = threading.Thread(target=stream_output, args=(port, proc, restart), daemon=True)
    thread.start()
    return proc


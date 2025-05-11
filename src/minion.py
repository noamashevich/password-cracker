from flask import Flask, request, jsonify
import hashlib
import argparse
import threading
from config_loader import load_config

# Create a Flask web application
app = Flask(__name__)

# Used to signal early stop of search
stop_event = threading.Event()

# Load configuration from config.json
CONFIG = load_config()
MINION_HOST = CONFIG["minion_host"]
START_PORT = CONFIG["start_port"]


class MinionCracker:
    """
    A class that performs hash cracking over a given numeric phone number range.
    """

    def __init__(self, target_hash: str, start_range: int, end_range: int):
        """
        Initializes a MinionCracker instance.

        :param target_hash: The MD5 hash we are trying to find the matching phone number for
        :param start_range: Starting number in the range (e.g., 500000000)
        :param end_range: Ending number in the range (e.g., 599999999)
        """
        self.target_hash = target_hash
        self.start_range = start_range
        self.end_range = end_range

    @staticmethod
    def format_phone(number: int) -> str:
        """
        Formats a numeric value into an Israeli phone number: '05X-XXXXXXX'.

        :param number: Phone number as an integer
        :return: Formatted phone number as a string
        """
        num_str = str(number).rjust(10, '0')
        return f"{num_str[:3]}-{num_str[3:]}"

    @staticmethod
    def md5_hash(s: str) -> str:
        """
        Returns the MD5 hash of a given string.

        :param s: The string to hash
        :return: MD5 hash string
        """
        return hashlib.md5(s.encode()).hexdigest()

    def crack_range(self) -> str | None:
        """
        Searches for a phone number in the specified range whose MD5 hash matches the target.

        This loop can be stopped early if stop_event is triggered.

        :return: The matching phone number, or None if not found
        """
        print(f"Searching for {self.target_hash} in range {self.start_range} to {self.end_range}", flush=True)
        for num in range(self.start_range, self.end_range + 1):
            if stop_event.is_set():
                # Another minion already found the password
                break

            phone = self.format_phone(num)
            hashed = self.md5_hash(phone)
            if hashed == self.target_hash:
                print(f"FOUND: {phone}", flush=True)
                return phone
        return None


@app.route("/crack", methods=["POST"])
def crack():
    """
    Endpoint that receives a cracking request and tries to find a matching phone number.

    Expected JSON payload:
    {
        "target_hash": "md5_hash_value",
        "range_start": 500000000,
        "range_end": 509999999
    }

    :return: JSON result with status:
        - {"status": "found", "password": "<phone>"} if found
        - {"status": "not_found"} if no match
        - {"status": "error", "message": "..."} if something went wrong
    """
    try:
        stop_event.clear()  # Reset stop signal before each new search

        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON"}), 400

        cracker = MinionCracker(
            target_hash=data["target_hash"],
            start_range=int(data["range_start"]),
            end_range=int(data["range_end"])
        )

        result = cracker.crack_range()
        if result:
            return jsonify({"status": "found", "password": result})
        return jsonify({"status": "not_found"})

    except Exception as e:
        print(f"Error while processing request: {e}", flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/stop", methods=["POST"])
def stop():
    """
    Endpoint that allows the master to stop the current cracking operation.

    When this is called, the stop_event will be set, and the running loop (if any) will stop.
    This does not shut down the server, only stops the current search.
    """
    stop_event.set()
    return jsonify({"status": "ok", "message": "Stopping current work"})


if __name__ == "__main__":
    # Parse the port from command line arguments (used when launching each minion)
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=START_PORT)
    args = parser.parse_args()

    print(f"Minion running on port {args.port}", flush=True)

    # Start the Flask server
    app.run(host=MINION_HOST, port=args.port)

from flask import Flask, request, jsonify
import hashlib
import argparse

app = Flask(__name__)


class MinionCracker:
    def __init__(self, target_hash: str, start_range: int, end_range: int):
        self.target_hash = target_hash
        self.start_range = start_range
        self.end_range = end_range

    @staticmethod
    def format_phone(number: int) -> str:
        """
        Formats a number into Israeli phone format '05X-XXXXXXX'.

        Pads with leading zeros if needed to ensure 10 digits.

        :param number: A numeric value representing a phone number (e.g., 500000001).
        :return: Formatted phone number as a string: '050-0000001'

        Example:
        >>> format_phone(500000001)
        '050-0000001'
        """
        num_str = str(number).rjust(10, '0')
        return f"{num_str[:3]}-{num_str[3:]}"

    @staticmethod
    def md5_hash(s: str) -> str:
        """
        Computes the MD5 hash of a given string and returns it as a hexadecimal string.

        :param s: The input string to be hashed.
        :return: A 32-character MD5 hash string.

        Example:
        >>> md5_hash("050-0000001")
        '0da74e79f730b74d0b121f6817b13eac'
        """
        return hashlib.md5(s.encode()).hexdigest()

    def crack_range(self):
        """
        Goes threw all the numbers in the current range -> adjusts the number to valid phone number
        -> hashes the password and checks if it matches to the target hash

        :param target_hash: The MD5 password we want to find it real number
        :param start: Start phone number range
        :param end: End phone number range
        :return: If found -> the right phone number. else, None

        Example:
        >>> crack_range("0da74e79f730b74d0b121f6817b13eac", 50000000, 544444444)
        '050-0000001'
        """
        print(f"Searching for {self.target_hash} in range {self.start_range} to {self.end_range}", flush=True)
        for num in range(self.start_range, self.end_range + 1):
            phone = self.format_phone(num)
            hashed = self.md5_hash(phone)
            # print(f"Checking {phone} -> {hashed}", flush=True)
            if hashed == self.target_hash:
                print(f"FOUND: {phone}", flush=True)
                return phone
        print("Not found in range.", flush=True)
        return None


@app.route("/crack", methods=["POST"])
def crack():
    """
    Handles a POST request to attempt cracking a given MD5 hash, with the current range
    Expected JSON payload:
    {
        "target_hash": "MD5 hash string",
        "range_start": integer,
        "range_end": integer
    }
    :return:
        - {"status": "found", "password": "05X-XXXXXXX"} if match is found
        - {"status": "not_found"} if no match is found in the range
        - {"status": "error", "message": "<error_message>"} in case of failure
    """
    try:
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()
    print(f"Minion running on port {args.port}", flush=True)
    app.run(host="127.0.0.1", port=args.port)
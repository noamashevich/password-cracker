from flask import Flask, request, jsonify
import hashlib
import argparse

app = Flask(__name__)

def format_phone(number: int) -> str:
    num_str = str(number).rjust(10, '0')  # מוודא שיש 10 ספרות
    return f"{num_str[:3]}-{num_str[3:]}"  # מחזיר 050-0000001

def md5_hash(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()

def crack_range(target_hash: str, start: int, end: int):
    print(f"🔍 Searching for {target_hash} in range {start} to {end}")
    for num in range(start, end + 1):
        phone = format_phone(num)
        hashed = md5_hash(phone)
        print(f"Checking {phone} → {hashed}")
        if hashed == target_hash:
            print(f"FOUND: {phone}")
            return phone
    print("Not found in range.")
    return None

@app.route("/crack", methods=["POST"])
def crack():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON"}), 400

        print("Received request:", data)
        target_hash = data["target_hash"]
        start = int(data["range_start"])
        end = int(data["range_end"])
        result = crack_range(target_hash, start, end)
        if result:
            return jsonify({"status": "found", "password": result})
        return jsonify({"status": "not_found"})
    except Exception as e:
        print(f"Error while processing request: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()
    print(f"Minion running on port {args.port}")
    app.run(host="127.0.0.1", port=args.port)
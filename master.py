import requests
import time

NUM_MINIONS = 4
MINION_URLS = [
    "http://127.0.0.1:5001/crack",
    "http://127.0.0.1:5002/crack",
    "http://127.0.0.1:5003/crack",
    "http://127.0.0.1:5004/crack"
]

PHONE_START = 500000000
PHONE_END = 599999999

def split_ranges(start: int, end: int, num_parts: int):
    total = end - start + 1
    chunk = total // num_parts
    ranges = []

    for i in range(num_parts):
        range_start = start + i * chunk
        range_end = start + (i + 1) * chunk - 1
        if i == num_parts - 1:
            range_end = end  # שלא ילך לאיבוד
        ranges.append((range_start, range_end))

    return ranges

def crack_hash(target_hash: str):
    print(f"Cracking hash: {target_hash}")
    ranges = split_ranges(PHONE_START, PHONE_END, NUM_MINIONS)

    for i, (start, end) in enumerate(ranges):
        payload = {
            "target_hash": target_hash,
            "range_start": start,
            "range_end": end
        }
        try:
            # Sending POST requests to  the minion servers
            response = requests.post(MINION_URLS[i], json=payload, timeout=180)
            print(response)
            print(payload)
            print(MINION_URLS[i])
            data = response.json()
            if data["status"] == "found":
                print(f"Found password: {data['password']}")
                return data["password"]
        except Exception as e:
            print(f"Failed to contact Minion {i+1}: {e}")
    return None

def main():
    with open("hashes.txt", "r") as f:
        hashes = [line.strip() for line in f if line.strip()]

    results = []

    for h in hashes:
        password = crack_hash(h)
        results.append(f"{h} => {password if password else 'NOT FOUND'}")

    with open("output.txt", "w") as f:
        f.write("\n".join(results))

    print("Done! Results saved to output.txt")

if __name__ == "__main__":
    main()

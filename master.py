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
    """
    Splits the phone numbers ranges for the minion servers
    :param start: Always will be PHONE_START = 500000000
    :param end: Always will be PHONE_END = 599999999
    :param num_parts: The number of the minion servers we want to execute
    :return: The range in array of tuples

    Example:
    >>> split_ranges(50000000, 599999999, 4)
    [(500000000, 524999999), (525000000, 549999999), (550000000, 574999999), (575000000, 599999999)]
    """
    total = end - start + 1
    chunk = total // num_parts
    ranges = []

    for i in range(num_parts):
        range_start = start + i * chunk
        range_end = start + (i + 1) * chunk - 1
        if i == num_parts - 1:
            range_end = end
        ranges.append((range_start, range_end))
    print(ranges)
    return ranges

def crack_hash(target_hash: str):
    """
    For each hash from hashes.txt:
    Finds the hashed phone number between all the possible numbers ->
    Goes thew the ranges (matching to the number of minion servers we should have) ->
    creating a payload json for the POST requests to the minion server
    and sends the request to the server by the right URL from MINION_URLS.
    Receives the not hashed password !

    :param target_hash: The current hash we want to find his real password
    :return: The not hashed password

    Example:
    >>> crack_hash("5da0547714d53db4a4c79bc11a057a19")
    050-0056708
    """
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

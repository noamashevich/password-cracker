from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import os
from config_loader import load_config

# Load configuration from config.json
CONFIG = load_config()

NUM_MINIONS = CONFIG["num_minions"]
PHONE_START = CONFIG["phone_start"]
PHONE_END = CONFIG["phone_end"]
MINION_HOST = CONFIG["minion_host"]
START_PORT = CONFIG["start_port"]


class MasterCracker:
    def __init__(self, minion_host: str, start_port: int, phone_start: int, phone_end: int, num_minions: int):
        self.minion_host = minion_host
        self.start_port = start_port
        self.phone_start = phone_start
        self.phone_end = phone_end
        self.num_minions = num_minions

    @staticmethod
    def split_ranges(start: int, end: int, num_parts: int) -> [()]:
        """
        Splits the phone number range evenly for the minion servers.
        :param start: Start range
        :param end: End range
        :param num_parts: The num of the minions
        :return: List of tuples of the current start and end range
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
        return ranges

    @staticmethod
    def send_request(target_hash: str, start: int, end: int, url: str) -> str:
        """
        Sends a cracking request to a single minion.
        :param target_hash: The current hash we want to discover
        :param start: Start range
        :param end: End range
        :param url: The url we want to send it POST request
        :return: The password
        """
        payload = {
            "target_hash": target_hash,
            "range_start": start,
            "range_end": end
        }
        try:
            response = requests.post(url, json=payload, timeout=180)
            data = response.json()
            if data["status"] == "found":
                return data["password"]
        except Exception as e:
            print(f"Failed to contact {url}: {e}")
        return None

    def crack_hash_parallel(self, target_hash):
        """
        Sends requests to all minions in parallel with ThreadPoolExecutor,
        Creating an array of requests and then going threw all the requests in parallel
        Returns the first successful result.
        :param target_hash: The current hash we want to discover
        :return: The real password incase we found it. None if not
        """
        print(f"Cracking hash: {target_hash}")
        ranges = self.split_ranges(self.phone_start, self.phone_end, self.num_minions)

        with ThreadPoolExecutor(max_workers=self.num_minions) as executor:
            futures = []
            for i, (start, end) in enumerate(ranges):
                url = f"http://{self.minion_host}:{self.start_port + i}/crack"
                futures.append(executor.submit(self.send_request, target_hash, start, end, url))

            for future in as_completed(futures):
                password = future.result()
                if password:
                    return password
        return None

    def run(self, input_file: str, output_file: str):
        """
        Reads hashes from file, cracks each one, and writes results to output file.
        If rerun, skips hashes already processed (crash recovery).
        :param input_file: The target file: hashes.txt
        :param output_file: The results file: output.txt
        """
        already_done = set()
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                for line in f:
                    parts = line.strip().split(" => ")
                    if len(parts) == 2:
                        already_done.add(parts[0])

        with open(input_file, "r") as f:
            hashes = [line.strip() for line in f if line.strip()]

        for h in hashes:
            if h in already_done:
                print(f"Skipping already processed hash: {h}")
                continue

            password = self.crack_hash_parallel(h)
            if password:
                print(f"Found password: {password}")
            else:
                print("Not found password :(")

            with open(output_file, "a") as f:
                f.write(f"{h} => {password if password else 'NOT FOUND'}\n")

        print("\nDone! Results saved to", output_file)


if __name__ == "__main__":
    cracker = MasterCracker(MINION_HOST, START_PORT, PHONE_START, PHONE_END, NUM_MINIONS)
    cracker.run("data/hashes.txt", "data/output.txt")

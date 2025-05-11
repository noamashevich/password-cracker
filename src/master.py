from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import requests
import os
from config_loader import load_config
from run_minions import launch_and_monitor

# Load configuration from config.json
CONFIG = load_config()
NUM_MINIONS = CONFIG["num_minions"]
PHONE_START = CONFIG["phone_start"]
PHONE_END = CONFIG["phone_end"]
MINION_HOST = CONFIG["minion_host"]
START_PORT = CONFIG["start_port"]


class MasterCracker:
    """
    Coordinates the password cracking process by launching minions, distributing tasks,
    collecting results, and handling crash recovery.
    """
    def __init__(self, minion_host: str, start_port: int, phone_start: int, phone_end: int, num_minions: int):
        self.minion_host = minion_host
        self.start_port = start_port
        self.phone_start = phone_start
        self.phone_end = phone_end
        self.num_minions = num_minions
        self.minion_processes = []

    def launch_minions(self):
        """
        Launches all minion processes and stores their references for later termination.
        """
        print("Launching minions...")
        for i in range(self.num_minions):
            port = self.start_port + i
            print(f"Minion on port {port} started.")
            proc = launch_and_monitor(port)
            self.minion_processes.append(proc)
        print("All minions launched.\n")

    def terminate_minions(self):
        """
        Terminates all minion processes launched by this master.
        """
        print("\nTerminating minions...")
        for proc in self.minion_processes:
            proc.terminate()
        print("All minions terminated.")

    @staticmethod
    def split_ranges(start: int, end: int, num_parts: int) -> list[tuple[int, int]]:
        """
        Splits a numeric range evenly into sub-ranges.

        :param start: The start of the range
        :param end: The end of the range
        :param num_parts: Number of parts (minions)
        :return: List of (start, end) tuples
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
    def send_request(target_hash: str, start: int, end: int, url: str) -> str | None:
        """
        Sends a cracking request to a specific minion.

        :param target_hash: The hash to crack
        :param start: Range start
        :param end: Range end
        :param url: Minion's URL
        :return: Cracked password or None
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

    def crack_hash_parallel(self, target_hash: str) -> str | None:
        """
        Sends the cracking task to all minions in parallel and returns the first successful result.

        Once a password is found, the master sends a /stop signal to all other minions to stop their search.

        :param target_hash: The MD5 hash to crack (e.g., '0da74e79f730b74d0b121f6817b13eac')
        :return: The cracked password (e.g., '050-1234567') if found, or None if not found
        """
        print(f"Cracking hash: {target_hash}")

        # Split the phone number range evenly between all minions
        ranges = self.split_ranges(self.phone_start, self.phone_end, self.num_minions)

        # Create a thread pool for parallel HTTP requests to minions
        with ThreadPoolExecutor(max_workers=self.num_minions) as executor:
            futures = []  # List of all submitted tasks
            future_to_port = {}  # Map each Future to the minion's port number

            for i, (start, end) in enumerate(ranges):
                port = self.start_port + i
                url = f"http://{self.minion_host}:{port}/crack"
                future = executor.submit(self.send_request, target_hash, start, end, url)
                futures.append(future)
                future_to_port[future] = port

            for future in as_completed(futures):
                password = future.result()
                if password:
                    found_port = future_to_port[future]
                    # Send stop signal to all other minions to stop their current cracking operation
                    for port in range(self.start_port, self.start_port + self.num_minions):
                        if port != found_port:
                            try:
                                stop_url = f"http://{self.minion_host}:{port}/stop"
                                requests.post(stop_url, timeout=3)
                            except Exception as e:
                                print(f"Could not stop minion on port {port}: {e}")

                    return password
        return None

    def run(self, input_file: str, output_file: str):
        """
        Orchestrates the entire cracking process, including crash recovery and writing results.

        :param input_file: Path to input file (hashes)
        :param output_file: Path to output file (results)
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
                print("Password not found.")

            with open(output_file, "a") as f:
                f.write(f"{h} => {password if password else 'NOT FOUND'}\n")

        print("\nDone! Results saved to", output_file)

if __name__ == "__main__":
    try:
        cracker = MasterCracker(MINION_HOST, START_PORT, PHONE_START, PHONE_END, NUM_MINIONS)
        cracker.launch_minions()
        cracker.run("data/hashes.txt", "data/output.txt")
    finally:
        cracker.terminate_minions()


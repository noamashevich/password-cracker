import json
import os

def load_config(path: str = "config/config.json") -> dict:
    """
    Loads the JSON configuration file.

    :param path: Path to the configuration file (default is 'config.json').
    :return: A dictionary with the configuration values.
    :raises FileNotFoundError: If the config file is not found.
    :raises json.JSONDecodeError: If the file is not a valid JSON.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found at: {path}")

    with open(path, "r") as f:
        return json.load(f)

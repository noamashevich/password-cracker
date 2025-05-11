# 📞 Password Cracker (Distributed System)

This project simulates a **distributed password-cracking system** using Python, Flask, and multi-threading.  
It is designed to crack hashed Israeli phone numbers in the format `05X-XXXXXXX` (e.g., `050-1234567`) that were hashed using **MD5**.

---

## 🚀 Features

-  **Parallel** password cracking with multiple workers ("minions")
-  **Crash handling**: restarts minions if they crash
-  **Resumable**: master won’t repeat already-cracked hashes
-  Fully configurable from `config/config.json`

---

## 📁 Project Structure

```
PasswordCracker/
├── config/
│   └── config.json         # Configuration settings (e.g., number of minions, ports)
├── data/
│   ├── hashes.txt          # Input file with MD5 hashes
│   └── output.txt          # Output file for cracked passwords
├── src/
│   ├── config_loader.py    # Loads config.json
│   ├── master.py           # Main controller: distributes work to minions
│   ├── minion.py           # Worker server: cracks password in a range
│   └── run_minions.py      # Launches and monitors all minion servers
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .gitignore              # Files/folders to ignore by Git
```

---

## 🧩 How It Works

- You provide a list of MD5 hashes in `data/hashes.txt`
- The **master** splits the range of possible phone numbers across **multiple minions**
- Each **minion** searches its assigned range and sends back the match (if found)
- Cracked passwords are saved to `data/output.txt`
- Crashes? Don’t worry – minions are restarted automatically!

---

## ⚙️ Installation

1. **Clone the project**
```bash
git clone https://github.com/YOUR_USERNAME/PasswordCracker.git
cd PasswordCracker
Create and activate a virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate
Install dependencies
pip install -r requirements.txt'
```
---
## 🔧 Configuration
```
Edit config/config.json:
{
  "num_minions": 4,
  "start_port": 5001,
  "minion_host": "127.0.0.1",
  "phone_start": 500000000,
  "phone_end": 599999999
}
```
- num_minions: How many minion servers to run
- start_port: First port (others will increment from here)
- minion_host: Usually 127.0.0.1
- phone_start, phone_end: Full phone range to check
---
## 📂 Input & Output
### Input: `data/hashes.txt`
#### Add one MD5 hash per line:
e99a18c428cb38d5f260853678922e03
5da0547714d53db4a4c79bc11a057a19

### output: `data/output.txt`
#### The cracked results:
e99a18c428cb38d5f260853678922e03 => 050-1234567
5da0547714d53db4a4c79bc11a057a19 => NOT FOUND
---
## 🧪 How to Run
### 1. Start the minion servers (in one terminal):
`python src/run_minions.py`
This launches all minions (Flask servers) and restarts them automatically if they crash.

### 2. Run the master (in a separate terminal):
`python src/master.py`

#### The master will:
- Read hashes from data/hashes.txt
- the cracking task across minions in parallel
- Save results to data/output.txt
- Avoid repeating already solved hashes
---
## 💥 Crash Handling
- Minion crashes: Restarted automatically using run_minions.py
- Master crashes: When restarted, it skips already processed hashes in output.txt

You can simulate a minion crash by inserting this line inside minion.py:
```
if random.random() < 0.01:
    os._exit(1)
```
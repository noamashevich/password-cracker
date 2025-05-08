import hashlib

def analyze_string(s):
    print("🔍 Input string:", repr(s))
    print("🔢 Length:", len(s))
    print("🔐 MD5 hash:", hashlib.md5(s.encode()).hexdigest())
    print("🧩 Character breakdown:")
    for i, c in enumerate(s):
        print(f"  Index {i}: '{c}' (ord: {ord(c)})")

def main():
    print("=== HASH DEBUG TOOL ===")
    s = input("Enter phone string (e.g. 050-0000001): ").strip()
    analyze_string(s)

if __name__ == "__main__":
    main()

import hashlib
from minion import  *

if __name__ == '__main__':
    import hashlib


    def format_phone(n: int) -> str:
        s = str(n).rjust(10, "0")
        return f"{s[:3]}-{s[3:]}"

    phone = format_phone(500000001)
    print(phone)  # 050-0000001
    print(hashlib.md5(phone.encode()).hexdigest())
    #
    # s1 = "050-0000001"
    # s2 = " 050-0000001 "  # עם רווחים
    #
    # print("clean :", hashlib.md5(s1.encode()).hexdigest())
    # print("padded:", hashlib.md5(s2.encode()).hexdigest())
    #
    # for i, c in enumerate(s1):
    #     print(f"Index {i}: {repr(c)} → ASCII {ord(c)}")
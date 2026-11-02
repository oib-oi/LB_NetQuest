"""5. frames — 7005/tcp: бинарные кадры, 30 раундов за 60 секунд."""
import struct
from functools import reduce
from common import Conn, get_id

HDR = struct.Struct("!2sBI")  # magic(2) type(uint8) length(uint32)
QUESTION, ANSWER, NOISE, RESULT, ERROR = 1, 2, 3, 4, 5

c = Conn(7005, timeout=15)
c.login(get_id())
c.read_until(b"BINARY\n")      # дальше только бинарные кадры


def send_frame(ftype, payload):
    c.s.sendall(HDR.pack(b"NQ", ftype, len(payload)) + payload)


rounds = 0
while True:
    magic, ftype, length = HDR.unpack(c.read_exact(HDR.size))
    if magic != b"NQ":
        raise ValueError(f"bad magic {magic!r}")
    payload = c.read_exact(length)

    if ftype == QUESTION:
        op, n = struct.unpack_from("!BH", payload, 0)
        nums = struct.unpack_from(f"!{n}i", payload, 3)
        if op == 1:
            res = sum(nums)
        elif op == 2:
            res = max(nums)
        elif op == 3:
            res = min(nums)
        elif op == 4:
            res = reduce(lambda x, y: x ^ y, nums, 0)
        else:
            raise ValueError(f"unknown op {op}")
        send_frame(ANSWER, struct.pack("!q", res))
        rounds += 1
        print(f"round {rounds}: op={op} n={n} -> {res}")
    elif ftype == NOISE:
        continue
    elif ftype == RESULT:
        print("RESULT:", payload.decode(errors="replace"))
        break
    elif ftype == ERROR:
        print("ERROR:", payload.decode(errors="replace"))
        break
    else:
        print(f"unknown frame type {ftype}, skipping")

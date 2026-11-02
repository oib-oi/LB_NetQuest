"""1. math — 7001/tcp: 100 примеров за 30 секунд."""
import re
from common import Conn, get_id

OPS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a // b,   # целочисленное деление
    "%": lambda a, b: a % b,
}
# Ищем вопрос прямо в буфере: строка может прийти без \n в конце
PAT = re.compile(rb"Q\s*(\d+)\s*/\s*(\d+)\s*:\s*(-?\d+)\s*([-+*/%])\s*(-?\d+)\s*=\s*\?")

c = Conn(7001)
c.login(get_id())

try:
    while True:
        m = PAT.search(c.buf)
        if not m:
            c._fill()
            continue
        c.buf = c.buf[m.end():]
        num, total = int(m[1]), int(m[2])
        a, op, b = int(m[3]), m[4].decode(), int(m[5])
        c.send_line(str(OPS[op](a, b)))
        if num == total:
            break
except ConnectionError:
    pass

print(c.read_rest(3))

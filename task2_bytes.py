"""2. bytes — 7002/tcp: посчитать байты после BEGIN\\n до 3 с тишины."""
import socket
from common import Conn, get_id

c = Conn(7002)
c.login(get_id())

c.read_until(b"BEGIN\n")
count = len(c.buf)          # то, что пришло в одном recv вместе с BEGIN
c.buf = b""

c.s.settimeout(3)           # 3 секунды тишины = конец передачи
try:
    while True:
        chunk = c.s.recv(65536)
        if not chunk:
            break
        count += len(chunk)
except socket.timeout:
    pass
c.s.settimeout(c.timeout)

print("received bytes:", count)
c.send_line(str(count))
print(c.read_rest(3))

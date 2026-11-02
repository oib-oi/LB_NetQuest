"""4. udp — 7004/udp: собрать сообщение из кусков с потерями и дублями."""
import socket
from common import HOST, get_id

ID = get_id()
ADDR = (HOST, 7004)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(1.0)

parts = {}
total = None


def send(text):
    s.sendto((text + "\n").encode(), ADDR)


send(f"GET {ID}")
for attempt in range(100):
    try:
        while True:
            data, _ = s.recvfrom(65535)
            head, sep, payload = data.partition(b"|")
            try:
                seq, tot = map(int, head.split(b"/"))
            except ValueError:
                print("[server]", data)
                continue
            total = tot
            parts.setdefault(seq, payload)   # дубли игнорируем
    except socket.timeout:
        pass

    if total is None:          # потерялось всё — просим заново
        send(f"GET {ID}")
        continue
    missing = [i for i in range(total) if i not in parts]
    if not missing:
        break
    print(f"have {len(parts)}/{total}, missing: {missing}")
    for k in range(0, len(missing), 50):   # не раздуваем датаграмму
        send(f"RESEND {ID} " + ",".join(map(str, missing[k:k + 50])))
else:
    print("gave up")

if total is not None and len(parts) == total:
    msg = b"".join(parts[i] for i in range(total))
    print(msg.decode(errors="replace"))

"""3. latency — 7003/tcp: оценить постоянную часть задержки."""
import socket
import statistics
import time
from common import HOST, Conn, get_id

N = 60       # нужно >= 20; больше замеров — минимум ближе к истине
N_NET = 20   # замеров чистой сетевой задержки

# RTT PING/PONG = сеть + постоянная часть сервера + джиттер.
# Сетевую часть меряем временем TCP-рукопожатия (connect): его делает ядро
# сервера, без искусственной задержки. Это аналог утилиты ping.
net = []
for _ in range(N_NET):
    t0 = time.perf_counter()
    socket.create_connection((HOST, 7003), timeout=10).close()
    net.append((time.perf_counter() - t0) * 1000)
net_rtt = min(net)
print(f"network RTT (TCP handshake): min={net_rtt:.2f}  "
      f"median={statistics.median(net):.2f} ms")

c = Conn(7003, timeout=60)  # джиттер бывает очень большим
c.login(get_id())

rtts = []
for i in range(N):
    t0 = time.perf_counter()
    c.send_line(f"PING {i}")
    while True:
        line = c.read_line()
        if line.strip() == f"PONG {i}":
            break
        print("[server]", line)
    rtt = (time.perf_counter() - t0) * 1000
    rtts.append(rtt)
    print(f"{i:2d}: {rtt:8.2f} ms")

print(f"min={min(rtts):.2f}  median={statistics.median(rtts):.2f}  "
      f"mean={statistics.mean(rtts):.2f}  max={max(rtts):.2f}")

# Джиттер >= 0, значит минимум ближе всего к постоянной части;
# вычитаем из него сетевую задержку (тоже минимум — по той же причине)
answer = round(min(rtts) - net_rtt)
print("answer:", answer)
c.send_line(f"ANSWER {answer}")
print(c.read_rest(3))

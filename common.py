"""Общие функции для всех клиентов NetQuest."""
import socket
import sys

HOST = "153.76.167.185"


def get_id():
    if len(sys.argv) < 2:
        sys.exit(f"usage: python {sys.argv[0]} <your_id>")
    return sys.argv[1].strip().lower()


class Conn:
    """TCP-соединение с собственным буфером.

    Один recv() != один send() на сервере, поэтому всё, что пришло,
    складываем в self.buf и уже из него вырезаем строки / нужное число байт.
    """

    def __init__(self, port, timeout=10):
        self.s = socket.create_connection((HOST, port), timeout=timeout)
        self.timeout = timeout
        self.buf = b""

    def _fill(self):
        chunk = self.s.recv(65536)
        if not chunk:
            raise ConnectionError("server closed connection")
        self.buf += chunk

    def read_until(self, delim=b"\n"):
        while delim not in self.buf:
            self._fill()
        i = self.buf.index(delim) + len(delim)
        data, self.buf = self.buf[:i], self.buf[i:]
        return data

    def read_line(self):
        return self.read_until(b"\n").decode(errors="replace").rstrip("\r\n")

    def read_exact(self, n):
        while len(self.buf) < n:
            self._fill()
        data, self.buf = self.buf[:n], self.buf[n:]
        return data

    def send_line(self, text):
        self.s.sendall((text + "\n").encode())

    def read_rest(self, wait=2.0):
        """Забрать всё, что сервер пришлёт за `wait` секунд тишины."""
        self.s.settimeout(wait)
        out, self.buf = self.buf, b""
        try:
            while True:
                chunk = self.s.recv(65536)
                if not chunk:
                    break
                out += chunk
        except socket.timeout:
            pass
        finally:
            self.s.settimeout(self.timeout)
        return out.decode(errors="replace")

    def login(self, my_id):
        """Читаем приветствие до приглашения 'ID: ' и отправляем ID."""
        greeting = self.read_until(b"ID: ").decode(errors="replace")
        print("[server]", greeting.strip())
        self.send_line(my_id)

from socket import socket, SocketType, AF_INET, SOCK_STREAM
import struct


class SocketClient(object):
    recv_format: str
    recv_size: int
    port: int

    _instance = None

    @classmethod
    def Singleton(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, port: int = 0) -> None:
        # Initialize client socket.
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.port = port
        self.init()

    def init(self) -> None:
        pass

    def start(self) -> None:
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.connect(('localhost', self.port))

    def stop(self) -> None:
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @property
    def recv_format(self) -> str:
        return 'i'

    @property
    def recv_size(self) -> int:
        return struct.calcsize(self.recv_format)

    def send_data(self) -> tuple:
        """
        Receive data from client.

        :param client: Client socket.
        :return: Received data.
        """
        if self.socket is None:
            return
        # Receive data from client.
        self.socket.sendall(
            self.pack_data(
                self.prepare_data()
            )
        )

    def pack_data(self, data: tuple) -> bytes:
        """
        Unpack received data.

        :param data: Received data.
        :return: Unpacked data.
        """
        if not data:
            return None

        # Unpack received data.
        return struct.pack(self.recv_format, *data)

    def prepare_data(self) -> tuple:
        return ()

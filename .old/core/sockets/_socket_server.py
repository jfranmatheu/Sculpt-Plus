from socket import socket, AF_INET, SOCK_STREAM
import struct


class SocketServer(object):
    ''' Listener socket server. '''
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
        self.connection = None
        self.init()

    def init(self) -> None:
        pass

    def start(self) -> None:
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('localhost', self.port))
        self.socket.listen()
        if self.port == 0:
            self.port = self.socket.getsockname()[1]
    
    def stop(self) -> None:
        self.socket.close()
        if self.connection is not None:
            self.connection.close()

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

    def receive_data(self, client: socket) -> tuple:
        """
        Receive data from client.

        :param client: Client socket.
        :return: Received data.
        """
        # Receive data from client.
        return self.unpack_data(
            client.recv(self.recv_size)
        )

    def unpack_data(self, data: bytes) -> tuple:
        """
        Unpack received data.

        :param data: Received data.
        :return: Unpacked data.
        """
        if not data:
            return None

        # Unpack received data.
        return struct.unpack(self.recv_format, data)

    def process_data(self, *data: tuple) -> str:
        pass

    def on_process_data(self, *data: tuple) -> None:
        pass

    def run(self) -> None:
        while True:
            conn, addr = self.socket.accept()
            # client_socket.setblocking(False)
            with conn:
                print ('Got connection from', addr)
                while True:
                    data = self.receive_data(conn)
                    if not data:
                        break
                    res = self.process_data(*data)
                    self.on_process_data(*data)
                    # client_socket.send(data)
                    # client_socket.setblocking(True)
                    if res in {'FINISHED', 'CANCELLED'}:
                        return

    def run_in_modal(self) -> str:
        if not self.connection:
            conn, addr = self.socket.accept()
            self.connection = conn
            print ('Got connection from', addr)
        else:
            conn = self.connection
        try:
            data = self.receive_data(conn)
            if not data:
                self.connection = None
                return 'FINISHED'
            res = self.process_data(*data)
            self.on_process_data(*data)
            if res in {'FINISHED', 'CANCELLED'}:
                self.connection = None
                return res
        except Exception as e:
            print(e)
            self.connection = None
        return 'RUNNING_MODAL'

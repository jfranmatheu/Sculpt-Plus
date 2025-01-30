from ._socket_server import SocketServer


class PBarServer(SocketServer):
    progress: float
    on_progress_update: callable

    def init(self):
        self.on_progress_update = None
        self.progress = 0

    def set_update_callback(self, callback: callable):
        self.on_progress_update = callback

    def process_data(self, _progress: int) -> str:
        # print("[SERVER] Progress:", _progress)
        progress: float = _progress / 100.0
        self.progress = round(progress, 2)
        if _progress >= 100:
            self.progress = 1
            res = 'FINISHED'
        else:
            res = 'CONTINUE'
        if self.on_progress_update:
            self.on_progress_update(progress)
        return res

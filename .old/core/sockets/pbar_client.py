from ._socket_client import SocketClient


class PBarClient(SocketClient):
    progress: float
    progress_increment_rate: float

    def init(self) -> None:
        self.progress_cumulative = 0
        self.progress = 0 # number in range 0.0 to 1.0.
        self.progress_increment_rate = 0 # increment rate.

    def set_increment_rate(self, step_count: int = 100) -> None:
        self.progress_increment_rate = 1.0 / step_count

    def set_progress(self, progress: float) -> None:
        # if not variation, skip update...
        # this is to avoid spamming the server.
        self.progress_cumulative = progress
        if (progress - self.progress) < 0.01 and progress < 1.0:
            return
        self.progress = progress
        if self.progress >= 1.0:
            self.progress = 1.0
        try:
            self.send_data()
        except ConnectionAbortedError as e:
            print(e)
            self.stop()

    def complete(self, stop: bool = False) -> None:
        self.set_progress(1.0)
        if stop:
            self.stop()

    def update(self, progress: float) -> None:
        self.set_progress(progress * self.progress_increment_rate)

    def increase(self) -> None:
        self.set_progress(self.progress_cumulative + self.progress_increment_rate)

    def prepare_data(self) -> tuple:
        # print("[CLIENT] Progress:", self.progress)
        return (
            int(self.progress * 100),
        )

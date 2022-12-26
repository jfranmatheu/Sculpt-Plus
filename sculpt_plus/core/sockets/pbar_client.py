from ._socket_client import SocketClient


class PBarClient(SocketClient):
    progress: float
    progress_increment_rate: float

    def init(self) -> None:
        self.progress = 0 # number in range 0.0 to 1.0.
        self.progress_increment_rate = 0 # increment rate.

    def set_increment_rate(self, step_count: int) -> None:
        self.progress_increment_rate = 1.0 / step_count

    def set_progress(self, progress: float) -> None:
        self.progress = progress
        if self.progress >= .98:
            self.progress = 1.0
        self.send_data()

    def update(self, progress: float) -> None:
        self.set_progress(progress * self.progress_increment_rate)

    def increase(self) -> None:
        self.set_progress(self.progress + self.progress_increment_rate)

    def prepare_data(self) -> tuple:
        print("[CLIENT] Progress:", self.progress)
        return (
            int(self.progress * 100),
        )

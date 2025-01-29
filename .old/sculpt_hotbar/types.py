from enum import Enum


class Return(Enum):
    FINISH = 'FINISHED'
    RUN = 'RUNNING_MODAL'
    
    def __call__(self): return {self.value}

from enum import Enum


class CallEnum(Enum):
    @staticmethod
    def action(key: str, value):
        pass

    def __call__(self):
        return CallEnum.action(self.name, self.value)

class CallEnumValue(Enum):
    @staticmethod
    def action(value):
        pass

    def __call__(self):
        return CallEnumValue.action(self.value)

class CallEnumName(Enum):
    @staticmethod
    def action(key: str):
        pass

    def __call__(self):
        return CallEnumName.action(self.name)

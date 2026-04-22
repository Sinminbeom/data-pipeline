from abc import abstractmethod

from python_library.process.process import IProcess


class IBusProcess(IProcess):

    @abstractmethod
    def send_message_imdg(self, message: str) -> None: ...


class IStreamBusProcess(IBusProcess):

    @abstractmethod
    def publish_stream(self, message: str) -> None: ...

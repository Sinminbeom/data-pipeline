from common.event_bus.listener.stream_listener import StreamListener
from common.process.imdg_bus_process import IImdgBusProcess, ImdgBusProcess
from protocol.message.message import IMessage
from protocol.protocol_wrapper import ProtocolWrapper


class DownloaderManager(ImdgBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        self._stream_listener: StreamListener | None = None

    def on_init(self):
        super().on_init()
        self._stream_listener = StreamListener(self)
        self._stream_listener.start()

    @staticmethod
    def playable_list_request(process: IImdgBusProcess, wrapper: ProtocolWrapper, packet: IMessage):
        pass

    def action(self) -> None:
        pass

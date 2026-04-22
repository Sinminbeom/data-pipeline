from python_library.process.process import abProcess

from common.event_bus.listener.stream_listener import StreamListener
from common.process.bus_process import BusProcess
from protocol.message.packet import Packet


class DownloaderManager(BusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        self._stream_listener: StreamListener | None = None

    def on_init(self):
        super().on_init()
        self._stream_listener = StreamListener(self)
        self._stream_listener.start()

    @staticmethod
    def playable_list_request(process: abProcess, packet: Packet):
        pass

    def action(self) -> None:
        pass

from src.app.rest.websocket_server import WebsocketServer
from src.common.process.bus_process import BusProcess


class SocketIOProcess(BusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)

        self.websocket_server: WebsocketServer | None = None
        pass

    def action(self) -> None:
        pass


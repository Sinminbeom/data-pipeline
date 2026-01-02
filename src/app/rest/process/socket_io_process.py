from src.app.rest.websocket_server import SocketIOServer
from src.common.process.bus_process import BusProcess
from src.config.project_config import ProjectConfig


class SocketIOProcess(BusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)

        self.websocket_server: SocketIOServer | None = None
        pass

    def on_init(self):
        super().on_init()

        bind_ip = ProjectConfig.instance().bind_ip
        bind_port = ProjectConfig.instance().bind_port

        self.websocket_server = SocketIOServer(self, bind_ip, bind_port)
        self.websocket_server.start()
        






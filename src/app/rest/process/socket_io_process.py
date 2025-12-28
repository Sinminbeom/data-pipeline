from logger.app_logger import AppLogger

from src.app.rest.websocket_server import SocketIOServer
from src.common.process.bus_process import BusProcess
from src.config.project_config import ProjectConfig


class SocketIOProcess(BusProcess):
    def __init__(self, app_name, process_name):
        AppLogger.set_config("../conf/application_windows.conf", "socket-io-process")
        ProjectConfig.set_config("../conf/application_windows.conf")

        channel_name = ProjectConfig.instance().channel_name
        super().__init__(app_name, process_name, channel_name)

        self.websocket_server: SocketIOServer | None = None
        pass

    def on_init(self):
        super().on_init()
        AppLogger.set_config("../conf/application_windows.conf", "socket-io-process")
        ProjectConfig.set_config("../conf/application_windows.conf")

        print("111111111111111111111111")
        bind_ip = ProjectConfig.instance().bind_ip
        bind_port = ProjectConfig.instance().bind_port

        print("222222222222222222222222")

        self.websocket_server = SocketIOServer(self, bind_ip, bind_port)
        self.websocket_server.start()
        print("33333333333333333333333333333")
        






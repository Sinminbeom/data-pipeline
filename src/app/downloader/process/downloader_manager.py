from src.common.process.bus_process import BusProcess


class DownloaderManager(BusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        print(app_name, process_name)
        pass

    def action(self) -> None:
        pass


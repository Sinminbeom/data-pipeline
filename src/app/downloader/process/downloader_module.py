from src.common.process.queue_control_process import QueueControlProcess


class DownloaderModule(QueueControlProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        print(app_name, process_name)
        pass

    def action(self) -> None:
        pass


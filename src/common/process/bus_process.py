from src.common.process.queue_control_process import QueueControlProcess


class BusProcess(QueueControlProcess):
    def __init__(self, app_name: str, process_name: str) -> None:
        super().__init__(app_name, process_name)
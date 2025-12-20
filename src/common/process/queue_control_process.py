from src.common.process.step_process import StepProcess


class QueueControlProcess(StepProcess):
    def __init__(self, app_name: str, process_name: str) -> None:
        super().__init__(app_name, process_name)
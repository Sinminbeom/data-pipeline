from process.process import abProcess


class StepProcess(abProcess):
    def __init__(self, app_name: str, process_name: str) -> None:
        super().__init__(process_name)
        self.app_name = app_name
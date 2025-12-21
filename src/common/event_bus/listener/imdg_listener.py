from process.process import abProcess

from src.common.event_bus.listener.listener import abListener


class ImdgListener(abListener):
    def __init__(self, _parent_process: abProcess):
        super().__init__(_parent_process)
        pass
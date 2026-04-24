from python_library.process.process import IProcess

from common.process.queue_control_process import QueueControlProcess


class IBusProcess(IProcess):
    pass


class BusProcess(QueueControlProcess, IBusProcess):
    pass

from common.process.interfaces import IBusProcess
from common.process.queue_control_process import QueueControlProcess


class BusProcess(QueueControlProcess, IBusProcess):
    pass

from abc import ABC, abstractmethod

from pcaps.ipcap import IPCap


class IPCapDTO(IPCap, ABC):
    @abstractmethod
    def get_time_stamp(self): ...

    @abstractmethod
    def get_time_str(self): ...

    @abstractmethod
    def get_offset_time_stamp(self): ...

    @abstractmethod
    def get_accumulate_offset_time_stamp(self): ...

    @abstractmethod
    def get_no(self): ...

    @abstractmethod
    def get_data_payload(self): ...

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from common.process.bus_process import BusProcess, IBusProcess
from config.project_config import ProjectConfig
from define.define import E_COMMUNICATION_TYPE
from protocol.message.message import ResponseInfo

if TYPE_CHECKING:
    from common.event_bus.imdg_bus import ImdgBus


class IImdgBusProcess(IBusProcess):

    @abstractmethod
    def send_message_imdg(self, message: str) -> None: ...

    @abstractmethod
    def send_message_req_imdg(self, protocol_id, receiver: str, *args) -> None: ...

    @abstractmethod
    def send_message_rep_imdg(
        self,
        protocol_id,
        receiver: str,
        *args,
        response: ResponseInfo,
    ) -> None: ...


class ImdgBusProcess(BusProcess, IImdgBusProcess):
    def __init__(self, app_name: str, process_name: str) -> None:
        super().__init__(app_name, process_name)
        self.channel_name = ProjectConfig.instance().channel_name
        self._imdg_bus: ImdgBus | None = None

    def on_init(self):
        from common.event_bus.imdg_bus import ImdgBus

        super().on_init()
        self._imdg_bus = ImdgBus(self, self.channel_name)
        self._imdg_bus.start()

    def is_ignore(self, communication_type: E_COMMUNICATION_TYPE, receiver: str) -> bool:
        from protocol.protocol_owner import ProtocolOwner
        return not ProtocolOwner.is_owner(receiver, self.get_app_name(), self.name)

    def send_message_imdg(self, _message: str) -> None:
        self._imdg_bus.send_message_imdg_queue(_message)

    def send_message_req_imdg(self, protocol_id, receiver: str, *args) -> None:
        self._imdg_bus.send_message_req_imdg_queue(protocol_id, receiver, *args)

    def send_message_rep_imdg(
        self,
        protocol_id,
        receiver: str,
        *args,
        response: ResponseInfo,
    ) -> None:
        self._imdg_bus.send_message_rep_imdg_queue(protocol_id, receiver, *args, response=response)

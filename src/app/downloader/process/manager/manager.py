from __future__ import annotations

from typing import Optional

from common.process.imdg_bus_process import ImdgBusProcess
from protocol.message.message import IMessage
from protocol.protocol_wrapper import ProtocolWrapper

from app.downloader.process.manager.state import (
    E_DOWNLOADER_MANAGER_STATE,
    build_state_map,
)


class DownloaderManager(ImdgBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)

    def on_init(self):
        super().on_init()
        self.set_state_component(
            build_state_map(),
            E_DOWNLOADER_MANAGER_STATE.WAIT,
        )

    def get_current_state_id(self) -> Optional[E_DOWNLOADER_MANAGER_STATE]:
        if self._state_component is None:
            return None
        current = self._state_component.get_state_manager().get_current_state_id()
        if current is None:
            return None
        assert isinstance(current, E_DOWNLOADER_MANAGER_STATE)
        return current

    @staticmethod
    def playable_list_request(process: DownloaderManager, wrapper: ProtocolWrapper, packet: IMessage):
        from process_category.enum_category import E_CATE
        from protocol.protocol_meta import E_PROTOCOL_ID
        from protocol.protocol_owner import ProtocolOwner
        from protocol.protocol_code import E_CODE, make_response_info

        if process.get_current_state_id() != E_DOWNLOADER_MANAGER_STATE.WAIT:
            process.send_message_rep_imdg(
                E_PROTOCOL_ID.PLAYABLE_LIST_REP,
                ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE),
                None,
                None,
                response=make_response_info(E_CODE.INVALID_REQUEST),
            )
            return

        if process._state_component is not None:
            process._state_component.change_state(E_DOWNLOADER_MANAGER_STATE.PLAYABLE, state_param_dto=packet)

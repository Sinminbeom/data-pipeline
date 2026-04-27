from common.process.imdg_bus_process import ImdgBusProcess
from common.state.state_container import StateContainer
from protocol.message.message import IMessage
from protocol.protocol_wrapper import ProtocolWrapper

from app.downloader.process.manager.state import (
    E_DOWNLOADER_MANAGER_STATE,
    build_state_container,
)


class DownloaderManager(ImdgBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)

    def on_init(self):
        super().on_init()
        self.set_state_machine(
            build_state_container(),
            E_DOWNLOADER_MANAGER_STATE.WAIT,
        )

    def set_state_machine(
        self,
        state_container: StateContainer,
        init_state_key: E_DOWNLOADER_MANAGER_STATE,
    ) -> None:
        super().set_state_machine(state_container, init_state_key)

    def get_current_state_key(self) -> E_DOWNLOADER_MANAGER_STATE | None:
        if self._state_machine is None:
            return None
        return self._state_machine.current_key

    @staticmethod
    def playable_list_request(process: "DownloaderManager", wrapper: ProtocolWrapper, packet: IMessage):
        from process_category.enum_category import E_CATE
        from protocol.protocol_meta import E_PROTOCOL_ID
        from protocol.protocol_owner import ProtocolOwner
        from protocol.protocol_code import E_CODE, make_response_info

        if process.get_current_state_key() != E_DOWNLOADER_MANAGER_STATE.WAIT:
            process.send_message_rep_imdg(
                E_PROTOCOL_ID.PLAYABLE_LIST_REP,
                ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE),
                None,
                None,
                response=make_response_info(E_CODE.INVALID_REQUEST),
            )
            return

        process._state_machine.change(E_DOWNLOADER_MANAGER_STATE.PLAYABLE)

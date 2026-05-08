from __future__ import annotations

from typing import TYPE_CHECKING

from python_library.state import abState

from protocol.message.process.play import InrPlayReq

from app.streamer.process.module.state.helper.pcap_player import PcapPlayer

if TYPE_CHECKING:
    from app.streamer.process.module.module import StreamerModule


class PlayState(abState):
    """sensor 1개에 대한 PCAP 파일 read 흐름.

    Phase 1: read 완료 시 OK 응답 + WAIT 복귀. 실제 패킷 송출은 Phase 2.
    """
    owner: StreamerModule

    def on_enter(self):
        assert isinstance(self.state_param_dto, InrPlayReq)

    def on_leave(self): pass

    def on_proc_once(self):
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        assert isinstance(self.state_param_dto, InrPlayReq)
        sensor_id = self.owner.name

        player = PcapPlayer(
            storage_root=self.owner.get_storage_root(),
            storage_prefix=self.owner.get_storage_prefix(),
            vehicle_id=self.state_param_dto.vehicle_id,
            sensor_id=sensor_id,
            start_time=self.state_param_dto.start_time,
            end_time=self.state_param_dto.end_time,
        )

        if not player.read():
            self.__send_invalid_request(str(player.error))
            self.__transition_to_wait()
            return

        # TODO Phase 2: PcapSenderThread로 player.pool 송출
        self.owner.send_message_rep_inner_queue(
            E_PROTOCOL_ID.INR_PLAY_REP,
            E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER,
            response=make_response_info(E_CODE.OK),
        )
        self.__transition_to_wait()

    def on_proc_every_frame(self): pass

    def __send_invalid_request(self, reason: str) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        self.owner.send_message_rep_inner_queue(
            E_PROTOCOL_ID.INR_PLAY_REP,
            E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER,
            response=make_response_info(E_CODE.INVALID_REQUEST, reason=reason),
        )

    def __transition_to_wait(self) -> None:
        from app.streamer.process.module.state.state_enum import E_STREAMER_MODULE_STATE
        self.owner._state_component.change_state(E_STREAMER_MODULE_STATE.WAIT)

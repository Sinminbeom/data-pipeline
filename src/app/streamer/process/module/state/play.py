from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from python_library.state import abState

from config.project_config import ProjectConfig
from protocol.message.process.play import InrPlayReq

from app.streamer.process.module.state.helper.pcap_player import PcapPlayer

if TYPE_CHECKING:
    from app.streamer.process.module.module import StreamerModule


class PlayState(abState):
    """Reader/Sender 2 thread + Pool buffer로 PCAP 재생.

    PcapPlayer.start() → reader가 buffer threshold 도달하면 on_ready 발화
    → INR_PLAY_REP OK 응답. sender는 background로 계속 송출.
    """
    owner: StreamerModule

    def __init__(self, state_lists, state_id) -> None:
        super().__init__(state_lists, state_id)
        self._ready_fired: bool = False
        self._error: Optional[Exception] = None

    def on_enter(self):
        assert isinstance(self.state_param_dto, InrPlayReq)
        self._ready_fired = False
        self._error = None

    def on_leave(self):
        # player는 owner._player에 보존 — Pause/Seek/Close/Stop state에서 접근.
        pass

    def on_proc_once(self):
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        assert isinstance(self.state_param_dto, InrPlayReq)
        sensor_id = self.owner.name

        try:
            config = ProjectConfig.instance()
            target_ip, target_port = config.get_stream_output(sensor_id)
        except Exception as exc:
            self.__send_invalid_request(f"stream_output not configured: {exc}")
            self.__transition_to_wait()
            return

        player = PcapPlayer(
            storage_root=self.owner.get_storage_root(),
            storage_prefix=self.owner.get_storage_prefix(),
            vehicle_id=self.state_param_dto.vehicle_id,
            sensor_id=sensor_id,
            start_time=self.state_param_dto.start_time,
            end_time=self.state_param_dto.end_time,
            target_ip=target_ip,
            target_port=target_port,
            buffer_size=config.player_buffer_size,
            ready_threshold_seconds=config.player_reader_buffering_time,
            file_refind_count=config.player_file_refind_count,
            file_refind_sleep_time=config.player_file_refind_sleep_time,
            on_ready=self._on_ready,
            on_error=self._on_error,
        )
        self.owner.set_player(player)
        player.start()

    def on_proc_every_frame(self):
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        # error 발생 시 INVALID_REQUEST 응답
        if self._error is not None:
            self.__send_invalid_request(str(self._error))
            self._error = None
            self.__transition_to_wait()
            return

        # ready 발화 시 OK 응답 + WAIT 복귀 (sender는 background에서 계속)
        if self._ready_fired:
            self._ready_fired = False
            self.owner.send_message_rep_inner_queue(
                E_PROTOCOL_ID.INR_PLAY_REP,
                E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER,
                response=make_response_info(E_CODE.OK),
            )
            self.__transition_to_wait()

    def _on_ready(self, first_packet_time: float) -> None:
        """reader thread에서 호출 — main loop frame에서 처리하도록 flag만 세팅."""
        self._ready_fired = True

    def _on_error(self, exc: Exception) -> None:
        """reader/sender thread에서 호출 — main loop frame에서 처리."""
        self._error = exc

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

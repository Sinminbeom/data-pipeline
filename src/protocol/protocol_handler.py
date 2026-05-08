"""모든 receive handler dispatcher를 한 곳에 모은 라우팅 테이블.

- 시그니처는 모두 (process, wrapper, packet) 통일
- 비즈니스 로직은 각 process 클래스의 handle_* instance method로 위임
- duck typing — protocol_id가 여러 카테고리에 라우팅돼도 dispatcher는 1개

group dispatcher는 시그니처가 다른 (process, pair_state, packets).
"""
from __future__ import annotations

from protocol.inr_protocol_matcher.inr_pair_state import E_PROTOCOL_PAIR_STATE
from protocol.message.external.ui.close import PDCloseReq, PDCloseRep
from protocol.message.external.ui.pause import PDPauseReq, PDPauseRep
from protocol.message.external.ui.play import PDPlayReq, PDPlayRep
from protocol.message.external.ui.playable_list import PDPlayableListReq, PDPlayableListRep
from protocol.message.external.ui.seek import PDSeekReq, PDSeekRep
from protocol.message.imdg.close import CloseReq, CloseRep
from protocol.message.imdg.pause import PauseReq, PauseRep
from protocol.message.imdg.play import PlayReq, PlayRep
from protocol.message.imdg.playable_list import PlayableListReq, PlayableListRep
from protocol.message.imdg.seek import SeekReq, SeekRep
from protocol.message.message import IMessage
from protocol.message.process.close import InrCloseReq, InrCloseRep
from protocol.message.process.pause import InrPauseReq, InrPauseRep
from protocol.message.process.play import InrPlayReq, InrPlayRep
from protocol.message.process.playable_list import InrPlayableListReq, InrPlayableListRep
from protocol.message.process.seek import InrSeekReq, InrSeekRep
from protocol.protocol_wrapper import ProtocolWrapper


class ProtocolHandler:
    # ---------------------------
    # External (PD) — REST_SERVER 진입/송출
    # ---------------------------
    @staticmethod
    def pd_playable_list_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PDPlayableListReq)
        process.handle_playable_list_request(packet)

    @staticmethod
    def pd_playable_list_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PDPlayableListRep)
        process.handle_playable_list_response(packet)

    @staticmethod
    def pd_play_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PDPlayReq)
        process.handle_play_request(packet)

    @staticmethod
    def pd_play_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PDPlayRep)
        process.handle_play_response(packet)

    @staticmethod
    def pd_pause_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PDPauseReq)
        process.handle_pause_request(packet)

    @staticmethod
    def pd_pause_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PDPauseRep)
        process.handle_pause_response(packet)

    @staticmethod
    def pd_seek_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PDSeekReq)
        process.handle_seek_request(packet)

    @staticmethod
    def pd_seek_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PDSeekRep)
        process.handle_seek_response(packet)

    @staticmethod
    def pd_close_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PDCloseReq)
        process.handle_close_request(packet)

    @staticmethod
    def pd_close_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PDCloseRep)
        process.handle_close_response(packet)

    # ---------------------------
    # IMDG — 앱 간 통신
    # ---------------------------
    @staticmethod
    def playable_list_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PlayableListReq)
        process.handle_playable_list_request(packet)

    @staticmethod
    def playable_list_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PlayableListRep)
        process.handle_playable_list_response(packet)

    @staticmethod
    def play_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PlayReq)
        process.handle_play_request(packet)

    @staticmethod
    def play_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PlayRep)
        process.handle_play_response(packet)

    @staticmethod
    def pause_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PauseReq)
        process.handle_pause_request(packet)

    @staticmethod
    def pause_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, PauseRep)
        process.handle_pause_response(packet)

    @staticmethod
    def seek_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, SeekReq)
        process.handle_seek_request(packet)

    @staticmethod
    def seek_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, SeekRep)
        process.handle_seek_response(packet)

    @staticmethod
    def close_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, CloseReq)
        process.handle_close_request(packet)

    @staticmethod
    def close_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, CloseRep)
        process.handle_close_response(packet)

    # ---------------------------
    # PROCESS (INR) — 앱 내 통신
    # ---------------------------
    @staticmethod
    def inr_playable_list_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, InrPlayableListReq)
        process.handle_playable_list_request(packet)

    @staticmethod
    def inr_playable_list_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, InrPlayableListRep)
        process.handle_playable_list_response(packet)

    @staticmethod
    def inr_play_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, InrPlayReq)
        process.handle_play_request(packet)

    @staticmethod
    def inr_play_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, InrPlayRep)
        process.handle_play_response(packet)

    @staticmethod
    def inr_pause_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, InrPauseReq)
        process.handle_pause_request(packet)

    @staticmethod
    def inr_pause_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, InrPauseRep)
        process.handle_pause_response(packet)

    @staticmethod
    def inr_seek_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, InrSeekReq)
        process.handle_seek_request(packet)

    @staticmethod
    def inr_seek_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, InrSeekRep)
        process.handle_seek_response(packet)

    @staticmethod
    def inr_close_request(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, InrCloseReq)
        process.handle_close_request(packet)

    @staticmethod
    def inr_close_response(process, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(packet, InrCloseRep)
        process.handle_close_response(packet)

    # ---------------------------
    # Group dispatchers — 시그니처 다름 (process, pair_state, packets)
    # ---------------------------
    @staticmethod
    def inr_playable_list_response_group(process, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]):
        process.handle_playable_list_group_response(pair_state, packets)

    @staticmethod
    def inr_play_response_group(process, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]):
        process.handle_play_group_response(pair_state, packets)

    @staticmethod
    def inr_pause_response_group(process, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]):
        process.handle_pause_group_response(pair_state, packets)

    @staticmethod
    def inr_seek_response_group(process, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]):
        process.handle_seek_group_response(pair_state, packets)

    @staticmethod
    def inr_close_response_group(process, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]):
        process.handle_close_group_response(pair_state, packets)

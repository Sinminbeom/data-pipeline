"""모든 receive handler dispatcher를 한 곳에 모은 라우팅 테이블.

- dispatcher 시그니처는 (process: IProcess, wrapper, packet) — 호출자(라우팅 테이블)와의
  Callable contravariance를 만족시키기 위해 추상 base 타입 IProcess로 받는다.
- 함수 안에서 assert isinstance로 카테고리별 구체 타입 narrowing (C# 다운캐스트 의미론).
- 카테고리별 분할 — 같은 메시지라도 process 타입이 다르면 dispatcher 분리
  (예: play_request → bridge_play_request / streamer_play_request / downloader_play_request)

group dispatcher는 시그니처가 다른 (process, pair_state, packets).
"""
from __future__ import annotations

from python_library.process.process import IProcess

from app.downloader.process.manager.manager import DownloaderManager
from app.downloader.process.module.module import DownloaderModule
from app.message_bridge.process.message_bridge_process import MessageBridgeProcess
from app.rest.process.socket_io_process import SocketIOProcess
from app.streamer.process.manager.manager import StreamerManager
from app.streamer.process.module.module import StreamerModule
from protocol.inr_protocol_matcher.inr_pair_state import E_PROTOCOL_PAIR_STATE
from protocol.message.external.ui.close import PDCloseReq, PDCloseRep
from protocol.message.external.ui.pause import PDPauseReq, PDPauseRep
from protocol.message.external.ui.play import PDPlayReq, PDPlayRep
from protocol.message.external.ui.playable_list import PDPlayableListReq, PDPlayableListRep
from protocol.message.external.ui.seek import PDSeekReq, PDSeekRep
from protocol.message.external.ui.stop import PDStopReq, PDStopRep
from protocol.message.imdg.close import CloseReq, CloseRep
from protocol.message.imdg.pause import PauseReq, PauseRep
from protocol.message.imdg.play import PlayReq, PlayRep
from protocol.message.imdg.playable_list import PlayableListReq, PlayableListRep
from protocol.message.imdg.seek import SeekReq, SeekRep
from protocol.message.imdg.stop import StopReq, StopRep
from protocol.message.message import IMessage
from protocol.message.process.close import InrCloseReq, InrCloseRep
from protocol.message.process.pause import InrPauseReq, InrPauseRep
from protocol.message.process.play import InrPlayReq, InrPlayRep
from protocol.message.process.playable_list import InrPlayableListReq, InrPlayableListRep
from protocol.message.process.seek import InrSeekReq, InrSeekRep
from protocol.message.process.stop import InrStopReq, InrStopRep
from protocol.protocol_wrapper import ProtocolWrapper


class ProtocolHandler:
    # ============================================================
    # External (PD) — REST_SERVER (SocketIOProcess)
    # ============================================================
    @staticmethod
    def pd_playable_list_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, SocketIOProcess)
        assert isinstance(packet, PDPlayableListReq)
        process.handle_playable_list_request(packet)

    @staticmethod
    def pd_playable_list_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, SocketIOProcess)
        assert isinstance(packet, PDPlayableListRep)
        process.handle_playable_list_response(packet)

    @staticmethod
    def pd_play_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, SocketIOProcess)
        assert isinstance(packet, PDPlayReq)
        process.handle_play_request(packet)

    @staticmethod
    def pd_play_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, SocketIOProcess)
        assert isinstance(packet, PDPlayRep)
        process.handle_play_response(packet)

    @staticmethod
    def pd_pause_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, SocketIOProcess)
        assert isinstance(packet, PDPauseReq)
        process.handle_pause_request(packet)

    @staticmethod
    def pd_pause_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, SocketIOProcess)
        assert isinstance(packet, PDPauseRep)
        process.handle_pause_response(packet)

    @staticmethod
    def pd_seek_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, SocketIOProcess)
        assert isinstance(packet, PDSeekReq)
        process.handle_seek_request(packet)

    @staticmethod
    def pd_seek_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, SocketIOProcess)
        assert isinstance(packet, PDSeekRep)
        process.handle_seek_response(packet)

    @staticmethod
    def pd_close_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, SocketIOProcess)
        assert isinstance(packet, PDCloseReq)
        process.handle_close_request(packet)

    @staticmethod
    def pd_close_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, SocketIOProcess)
        assert isinstance(packet, PDCloseRep)
        process.handle_close_response(packet)

    @staticmethod
    def pd_stop_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, SocketIOProcess)
        assert isinstance(packet, PDStopReq)
        process.handle_stop_request(packet)

    @staticmethod
    def pd_stop_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, SocketIOProcess)
        assert isinstance(packet, PDStopRep)
        process.handle_stop_response(packet)

    # ============================================================
    # IMDG — 앱 간 통신
    # ============================================================
    # --- PlayableList ---
    @staticmethod
    def bridge_playable_list_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, MessageBridgeProcess)
        assert isinstance(packet, PlayableListReq)
        process.handle_playable_list_request(packet)

    @staticmethod
    def downloader_playable_list_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, DownloaderManager)
        assert isinstance(packet, PlayableListReq)
        process.handle_playable_list_request(packet)

    @staticmethod
    def bridge_playable_list_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, MessageBridgeProcess)
        assert isinstance(packet, PlayableListRep)
        process.handle_playable_list_response(packet)

    # --- Play ---
    @staticmethod
    def bridge_play_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, MessageBridgeProcess)
        assert isinstance(packet, PlayReq)
        process.handle_play_request(packet)

    @staticmethod
    def streamer_play_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerManager)
        assert isinstance(packet, PlayReq)
        process.handle_play_request(packet)

    @staticmethod
    def downloader_play_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, DownloaderManager)
        assert isinstance(packet, PlayReq)
        process.handle_play_request(packet)

    @staticmethod
    def bridge_play_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, MessageBridgeProcess)
        assert isinstance(packet, PlayRep)
        process.handle_play_response(packet)

    # --- Pause ---
    @staticmethod
    def bridge_pause_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, MessageBridgeProcess)
        assert isinstance(packet, PauseReq)
        process.handle_pause_request(packet)

    @staticmethod
    def streamer_pause_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerManager)
        assert isinstance(packet, PauseReq)
        process.handle_pause_request(packet)

    @staticmethod
    def bridge_pause_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, MessageBridgeProcess)
        assert isinstance(packet, PauseRep)
        process.handle_pause_response(packet)

    # --- Seek ---
    @staticmethod
    def bridge_seek_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, MessageBridgeProcess)
        assert isinstance(packet, SeekReq)
        process.handle_seek_request(packet)

    @staticmethod
    def streamer_seek_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerManager)
        assert isinstance(packet, SeekReq)
        process.handle_seek_request(packet)

    @staticmethod
    def bridge_seek_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, MessageBridgeProcess)
        assert isinstance(packet, SeekRep)
        process.handle_seek_response(packet)

    # --- Close ---
    @staticmethod
    def bridge_close_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, MessageBridgeProcess)
        assert isinstance(packet, CloseReq)
        process.handle_close_request(packet)

    @staticmethod
    def streamer_close_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerManager)
        assert isinstance(packet, CloseReq)
        process.handle_close_request(packet)

    @staticmethod
    def downloader_close_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, DownloaderManager)
        assert isinstance(packet, CloseReq)
        process.handle_close_request(packet)

    @staticmethod
    def bridge_close_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, MessageBridgeProcess)
        assert isinstance(packet, CloseRep)
        process.handle_close_response(packet)

    # --- Stop ---
    @staticmethod
    def bridge_stop_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, MessageBridgeProcess)
        assert isinstance(packet, StopReq)
        process.handle_stop_request(packet)

    @staticmethod
    def streamer_stop_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerManager)
        assert isinstance(packet, StopReq)
        process.handle_stop_request(packet)

    @staticmethod
    def downloader_stop_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, DownloaderManager)
        assert isinstance(packet, StopReq)
        process.handle_stop_request(packet)

    @staticmethod
    def bridge_stop_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, MessageBridgeProcess)
        assert isinstance(packet, StopRep)
        process.handle_stop_response(packet)

    # ============================================================
    # PROCESS (INR) request — 앱 내 통신 (Module)
    # ============================================================
    @staticmethod
    def inr_downloader_playable_list_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, DownloaderModule)
        assert isinstance(packet, InrPlayableListReq)
        process.handle_playable_list_request(packet)

    @staticmethod
    def inr_streamer_play_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerModule)
        assert isinstance(packet, InrPlayReq)
        process.handle_play_request(packet)

    @staticmethod
    def inr_downloader_play_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, DownloaderModule)
        assert isinstance(packet, InrPlayReq)
        process.handle_play_request(packet)

    @staticmethod
    def inr_streamer_pause_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerModule)
        assert isinstance(packet, InrPauseReq)
        process.handle_pause_request(packet)

    @staticmethod
    def inr_streamer_seek_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerModule)
        assert isinstance(packet, InrSeekReq)
        process.handle_seek_request(packet)

    @staticmethod
    def inr_streamer_close_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerModule)
        assert isinstance(packet, InrCloseReq)
        process.handle_close_request(packet)

    @staticmethod
    def inr_downloader_close_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, DownloaderModule)
        assert isinstance(packet, InrCloseReq)
        process.handle_close_request(packet)

    @staticmethod
    def inr_streamer_stop_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerModule)
        assert isinstance(packet, InrStopReq)
        process.handle_stop_request(packet)

    @staticmethod
    def inr_downloader_stop_request(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, DownloaderModule)
        assert isinstance(packet, InrStopReq)
        process.handle_stop_request(packet)

    # ============================================================
    # PROCESS (INR) response — 앱 내 통신 (Manager)
    # ============================================================
    @staticmethod
    def inr_downloader_playable_list_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, DownloaderManager)
        assert isinstance(packet, InrPlayableListRep)
        process.handle_playable_list_response(packet)

    @staticmethod
    def inr_streamer_play_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerManager)
        assert isinstance(packet, InrPlayRep)
        process.handle_play_response(packet)

    @staticmethod
    def inr_downloader_play_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, DownloaderManager)
        assert isinstance(packet, InrPlayRep)
        process.handle_play_response(packet)

    @staticmethod
    def inr_streamer_pause_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerManager)
        assert isinstance(packet, InrPauseRep)
        process.handle_pause_response(packet)

    @staticmethod
    def inr_streamer_seek_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerManager)
        assert isinstance(packet, InrSeekRep)
        process.handle_seek_response(packet)

    @staticmethod
    def inr_streamer_close_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerManager)
        assert isinstance(packet, InrCloseRep)
        process.handle_close_response(packet)

    @staticmethod
    def inr_downloader_close_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, DownloaderManager)
        assert isinstance(packet, InrCloseRep)
        process.handle_close_response(packet)

    @staticmethod
    def inr_streamer_stop_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, StreamerManager)
        assert isinstance(packet, InrStopRep)
        process.handle_stop_response(packet)

    @staticmethod
    def inr_downloader_stop_response(process: IProcess, wrapper: ProtocolWrapper, packet: IMessage):
        assert isinstance(process, DownloaderManager)
        assert isinstance(packet, InrStopRep)
        process.handle_stop_response(packet)

    # ============================================================
    # Group dispatchers (Manager) — 시그니처 다름 (process, pair_state, packets)
    # ============================================================
    @staticmethod
    def inr_downloader_playable_list_response_group(
        process: IProcess, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]
    ):
        assert isinstance(process, DownloaderManager)
        process.handle_playable_list_group_response(pair_state, packets)

    @staticmethod
    def inr_streamer_play_response_group(
        process: IProcess, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]
    ):
        assert isinstance(process, StreamerManager)
        process.handle_play_group_response(pair_state, packets)

    @staticmethod
    def inr_downloader_play_response_group(
        process: IProcess, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]
    ):
        assert isinstance(process, DownloaderManager)
        process.handle_play_group_response(pair_state, packets)

    @staticmethod
    def inr_streamer_pause_response_group(
        process: IProcess, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]
    ):
        assert isinstance(process, StreamerManager)
        process.handle_pause_group_response(pair_state, packets)

    @staticmethod
    def inr_streamer_seek_response_group(
        process: IProcess, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]
    ):
        assert isinstance(process, StreamerManager)
        process.handle_seek_group_response(pair_state, packets)

    @staticmethod
    def inr_streamer_close_response_group(
        process: IProcess, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]
    ):
        assert isinstance(process, StreamerManager)
        process.handle_close_group_response(pair_state, packets)

    @staticmethod
    def inr_downloader_close_response_group(
        process: IProcess, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]
    ):
        assert isinstance(process, DownloaderManager)
        process.handle_close_group_response(pair_state, packets)

    @staticmethod
    def inr_streamer_stop_response_group(
        process: IProcess, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]
    ):
        assert isinstance(process, StreamerManager)
        process.handle_stop_group_response(pair_state, packets)

    @staticmethod
    def inr_downloader_stop_response_group(
        process: IProcess, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]
    ):
        assert isinstance(process, DownloaderManager)
        process.handle_stop_group_response(pair_state, packets)

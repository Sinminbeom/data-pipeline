from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Mapping, ClassVar

from python_library.process.process import abProcess

from protocol.message.message import IMessage
from protocol.protocol_wrapper import ProtocolWrapper

ReceiverKey = Any
FactoryFn = Callable[..., IMessage]
DecoderFn = Callable[[str], IMessage]
HandlerFn = Callable[[abProcess, ProtocolWrapper, IMessage], Any]


class E_PROTOCOL_ID(Enum):
    PD_PLAYABLE_LIST_REQ = "PD_100"
    PLAYABLE_LIST_REQ = "100"
    PLAYABLE_LIST_REP = "101"
    INR_PLAYABLE_LIST_REQ = "-100"


@dataclass(frozen=True)
class ProtocolEntry:
    factory: FactoryFn
    decoder: DecoderFn
    receive_handlers: Mapping[ReceiverKey, HandlerFn] = field(default_factory=dict)
    inr_group_receive_handlers: Mapping[ReceiverKey, HandlerFn] = field(default_factory=dict)


class ProtocolMeta:
    """
    Static-style registry.

    Usage:
      ProtocolMeta.initialize()  # once (or auto-called at module import)
      handler = ProtocolMeta.get_receive_handler(E_PROTOCOL_ID.PLAYABLE_LIST_REQ, E_CATE.DOWNLOADER)
    """

    table: ClassVar[Dict[E_PROTOCOL_ID, ProtocolEntry]] = {}
    _initialized: ClassVar[bool] = False

    # ---------------------------
    # Initialization
    # ---------------------------
    @classmethod
    def initialize(cls) -> None:
        """Idempotent init. Safe to call multiple times."""
        if cls._initialized:
            return
        cls._register_protocols()
        cls._initialized = True

    # ---------------------------
    # Register (private)
    # ---------------------------
    @classmethod
    def _register(cls, protocol_id: E_PROTOCOL_ID, entry: ProtocolEntry) -> None:
        if protocol_id in cls.table:
            raise KeyError(f"Protocol already registered: {protocol_id}")
        cls.table[protocol_id] = entry

    @classmethod
    def _register_protocols(cls) -> None:
        from process_category.enum_category import E_CATE
        from app.rest.websocket_server import SocketIOServer
        from app.downloader.process.manager.manager import DownloaderManager
        from app.downloader.process.module.module import DownloaderModule
        from app.message_bridge.process.message_bridge_process import MessageBridgeProcess
        from protocol.message.external.ui.playable_list import PDPlayableListReq
        from protocol.message.imdg.playable_list import PlayableListReq, PlayableListRep
        from protocol.message.process.playable_list import InrPlayableListReq

        # PD (외부 통신, raw dataclass)
        cls._register(
            E_PROTOCOL_ID.PD_PLAYABLE_LIST_REQ,
            ProtocolEntry(
                factory=lambda sender, receiver, vehicle_id, sensor_id_list, start_time, end_time: PDPlayableListReq(
                    protocol_id=E_PROTOCOL_ID.PD_PLAYABLE_LIST_REQ.value,
                    sender=sender,
                    receiver=receiver,
                    vehicle_id=vehicle_id,
                    sensor_id_list=sensor_id_list,
                    start_time=start_time,
                    end_time=end_time,
                ),
                decoder=PDPlayableListReq.from_json,
                receive_handlers={
                    E_CATE.REST_SERVER: lambda process, wrapper, packet: SocketIOServer.playable_list_request(
                        process, wrapper, packet
                    ),
                },
            ),
        )

        # IMDG (앱 간 통신)
        cls._register(
            E_PROTOCOL_ID.PLAYABLE_LIST_REQ,
            ProtocolEntry(
                factory=lambda sender, receiver, vehicle_id, sensor_id_list, start_time, end_time: PlayableListReq(
                    protocol_id=E_PROTOCOL_ID.PLAYABLE_LIST_REQ.value,
                    sender=sender,
                    receiver=receiver,
                    vehicle_id=vehicle_id,
                    sensor_id_list=sensor_id_list,
                    start_time=start_time,
                    end_time=end_time,
                ),
                decoder=PlayableListReq.from_json,
                receive_handlers={
                    E_CATE.MESSAGE_BRIDGE: lambda process, wrapper, packet: (
                        MessageBridgeProcess.playable_list_request(process, wrapper, packet)
                    ),
                    E_CATE.DOWNLOADER: lambda process, wrapper, packet: (
                        DownloaderManager.playable_list_request(process, wrapper, packet)
                    ),
                },
            ),
        )

        # IMDG (앱 간 통신, RESPONSE)
        cls._register(
            E_PROTOCOL_ID.PLAYABLE_LIST_REP,
            ProtocolEntry(
                factory=lambda sender, receiver, sensor_id_list, section_list, response: PlayableListRep(
                    protocol_id=E_PROTOCOL_ID.PLAYABLE_LIST_REP.value,
                    sender=sender,
                    receiver=receiver,
                    sensor_id_list=sensor_id_list if sensor_id_list is not None else [],
                    section_list=section_list if section_list is not None else [],
                    response=response,
                ),
                decoder=PlayableListRep.from_json,
                receive_handlers={
                    # MESSAGE_BRIDGE에서 RESPONSE 받음 — 추후 필요 시 핸들러 추가
                },
            ),
        )

        # PROCESS (앱 내 통신)
        cls._register(
            E_PROTOCOL_ID.INR_PLAYABLE_LIST_REQ,
            ProtocolEntry(
                factory=lambda sender, receiver, vehicle_id, start_time, end_time: InrPlayableListReq(
                    protocol_id=E_PROTOCOL_ID.INR_PLAYABLE_LIST_REQ.value,
                    sender=sender,
                    receiver=receiver,
                    vehicle_id=vehicle_id,
                    start_time=start_time,
                    end_time=end_time,
                ),
                decoder=InrPlayableListReq.from_json,
                receive_handlers={
                    E_CATE.DOWNLOADER: lambda process, wrapper, packet: (
                        DownloaderModule.playable_list_request(process, wrapper, packet)
                    )
                },
            ),
        )

    # ---------------------------
    # Conversion helper
    # ---------------------------
    @classmethod
    def _to_enum(cls, protocol_id: E_PROTOCOL_ID | str) -> E_PROTOCOL_ID:
        if isinstance(protocol_id, E_PROTOCOL_ID):
            return protocol_id
        try:
            # Enum(value) 패턴: E_PROTOCOL_ID("PD_100") -> E_PROTOCOL_ID.PD_PLAYABLE_LIST_REQ
            return E_PROTOCOL_ID(protocol_id)
        except ValueError as e:
            raise KeyError(f"Unknown protocol_id: {protocol_id}") from e

    # ---------------------------
    # Public API
    # ---------------------------
    @classmethod
    def get_receive_handler_container(cls) -> Dict[E_PROTOCOL_ID, Mapping[ReceiverKey, HandlerFn]]:
        cls.initialize()
        return {pid: entry.receive_handlers for pid, entry in cls.table.items()}

    @classmethod
    def get_receive_handler(cls, protocol_id: E_PROTOCOL_ID | str, receiver: ReceiverKey) -> HandlerFn:
        cls.initialize()
        pid = cls._to_enum(protocol_id)
        from protocol.protocol_owner import ProtocolOwner
        app_name = ProtocolOwner.get_app_name(receiver) if isinstance(receiver, str) else receiver
        return cls.table[pid].receive_handlers[app_name]

    @classmethod
    def get_inr_group_receive_handler(cls, protocol_id: E_PROTOCOL_ID | str, receiver: ReceiverKey) -> HandlerFn:
        cls.initialize()
        pid = cls._to_enum(protocol_id)
        return cls.table[pid].inr_group_receive_handlers[receiver]

    @classmethod
    def get_protocol_factory(cls, protocol_id: E_PROTOCOL_ID | str) -> FactoryFn:
        cls.initialize()
        pid = cls._to_enum(protocol_id)
        return cls.table[pid].factory

    @classmethod
    def get_json_decoder(cls, protocol_id: E_PROTOCOL_ID | str) -> DecoderFn:
        cls.initialize()
        pid = cls._to_enum(protocol_id)
        return cls.table[pid].decoder

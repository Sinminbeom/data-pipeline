from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Mapping, ClassVar

from src.protocol.message.packet import E_PROTOCOL_MESSAGE_DIRECTION
from src.protocol.protocol_wrapper import ProtocolWrapper

ReceiverKey = Any
FactoryFn = Callable[..., Any]
DecoderFn = Callable[[Any], Any]
HandlerFn = Callable[[Any, Any, Any], Any]


class E_PROTOCOL_ID(Enum):
    PD_PLAYABLE_LIST_REQ = "PD_100"
    PLAYABLE_LIST_REQ = "100"
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
        from src.process_category.enum_category import E_CATE
        from src.app.rest.websocket_server import SocketIOServer
        from src.app.downloader.process.downloader_manager import DownloaderManager
        from src.app.downloader.process.downloader_module import DownloaderModule
        from src.app.message_bridge.process.message_bridge_process import MessageBridgeProcess
        from src.protocol.message.external.ui.playable_list import PDPlayableListReq
        from src.protocol.message.ipc.imdg.playable_list import PlayableListReq
        from src.protocol.message.ipc.inner.playable_list import InrPlayableListReq

        # PD
        cls._register(
            E_PROTOCOL_ID.PD_PLAYABLE_LIST_REQ,
            ProtocolEntry(
                factory=lambda sender, receiver, vehicle_id, sensor_id_list, start_time, end_time: PDPlayableListReq(
                    E_PROTOCOL_ID.PD_PLAYABLE_LIST_REQ.value,
                    sender,
                    receiver,
                    vehicle_id,
                    sensor_id_list,
                    start_time,
                    end_time,
                ),
                decoder=PDPlayableListReq.from_json,
                receive_handlers={
                    E_CATE.REST_SERVER: lambda process, protocol_wrapper, protocol_message: SocketIOServer.playable_list_request(
                        process, protocol_wrapper, protocol_message
                    ),
                },
            ),
        )

        # Normal
        cls._register(
            E_PROTOCOL_ID.PLAYABLE_LIST_REQ,
            ProtocolEntry(
                factory=lambda message_direction, sender, receiver, vehicle_id, sensor_id_list, start_time, end_time: PlayableListReq(
                    E_PROTOCOL_ID.PLAYABLE_LIST_REQ.value,
                    E_PROTOCOL_MESSAGE_DIRECTION(message_direction),
                    sender,
                    receiver,
                    vehicle_id,
                    sensor_id_list,
                    start_time,
                    end_time,
                ),
                decoder=PlayableListReq.from_json,
                receive_handlers={
                    E_CATE.MESSAGE_BRIDGE: lambda process, protocol_wrapper, protocol_message: (
                        MessageBridgeProcess.playable_list_request(process, protocol_wrapper, protocol_message)
                    ),
                    E_CATE.DOWNLOADER: lambda process, protocol_wrapper, protocol_message: (
                        DownloaderManager.playable_list_request(process, protocol_wrapper, protocol_message)
                    ),
                },
            ),
        )

        # INR
        cls._register(
            E_PROTOCOL_ID.INR_PLAYABLE_LIST_REQ,
            ProtocolEntry(
                factory=lambda sender, receiver, vehicle_id, start_time, end_time: InrPlayableListReq(
                    E_PROTOCOL_ID.INR_PLAYABLE_LIST_REQ.value,
                    sender,
                    receiver,
                    vehicle_id,
                    start_time,
                    end_time,
                ),
                decoder=InrPlayableListReq.from_json,
                receive_handlers={
                    E_CATE.DOWNLOADER: lambda process, protocol_wrapper, protocol_message: (
                        DownloaderModule.playable_list_request(process, protocol_wrapper, protocol_message)
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
        return cls.table[pid].receive_handlers[receiver]

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

    @classmethod
    def get_protocol_packet_message(cls, _protocol_message_object) -> str:
        return ProtocolWrapper.get_protocol_wrapper(_protocol_message_object).get_protocol_packet_message()

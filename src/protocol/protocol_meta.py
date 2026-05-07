from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Mapping, ClassVar

from python_library.process.process import abProcess

from protocol.inr_protocol_matcher.inr_pair_state import E_PROTOCOL_PAIR_STATE
from protocol.message.message import IMessage
from protocol.protocol_wrapper import ProtocolWrapper

ReceiverKey = Any
FactoryFn = Callable[..., IMessage]
DecoderFn = Callable[[str], IMessage]
HandlerFn = Callable[[abProcess, ProtocolWrapper, IMessage], Any]
GroupHandlerFn = Callable[[abProcess, E_PROTOCOL_PAIR_STATE, list[IMessage]], Any]


class E_PROTOCOL_ID(Enum):
    PD_PLAYABLE_LIST_REQ = "PD_100"
    PD_PLAYABLE_LIST_REP = "PD_101"
    PLAYABLE_LIST_REQ = "100"
    PLAYABLE_LIST_REP = "101"
    INR_PLAYABLE_LIST_REQ = "-100"
    INR_PLAYABLE_LIST_REP = "-101"

    PD_PLAY_REQ = "PD_200"
    PD_PLAY_REP = "PD_201"
    PLAY_REQ = "200"
    PLAY_REP = "201"
    INR_PLAY_REQ = "-200"
    INR_PLAY_REP = "-201"


@dataclass(frozen=True)
class ProtocolEntry:
    factory: FactoryFn
    decoder: DecoderFn
    receive_handlers: Mapping[ReceiverKey, HandlerFn] = field(default_factory=dict)
    inr_group_receive_handlers: Mapping[ReceiverKey, GroupHandlerFn] = field(default_factory=dict)


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
        from protocol.message.external.ui.play import PDPlayReq, PDPlayRep
        from protocol.message.external.ui.playable_list import PDPlayableListReq, PDPlayableListRep
        from protocol.message.imdg.play import PlayReq, PlayRep
        from protocol.message.imdg.playable_list import PlayableListReq, PlayableListRep
        from protocol.message.process.play import InrPlayReq, InrPlayRep
        from protocol.message.process.playable_list import InrPlayableListReq, InrPlayableListRep
        from protocol.protocol_handler import ProtocolHandler

        # ===== PlayableList 3계층 =====

        # PD_PLAYABLE_LIST_REQ → REST_SERVER
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
                    E_CATE.REST_SERVER: ProtocolHandler.pd_playable_list_request,
                },
            ),
        )

        # PD_PLAYABLE_LIST_REP → REST_SERVER (socket.io broadcast)
        cls._register(
            E_PROTOCOL_ID.PD_PLAYABLE_LIST_REP,
            ProtocolEntry(
                factory=lambda sender, receiver, sensor_id_list, section_list, code, code_nm, reason: PDPlayableListRep(
                    protocol_id=E_PROTOCOL_ID.PD_PLAYABLE_LIST_REP.value,
                    sender=sender,
                    receiver=receiver,
                    sensor_id_list=sensor_id_list if sensor_id_list is not None else [],
                    section_list=section_list if section_list is not None else [],
                    code=code,
                    code_nm=code_nm,
                    reason=reason,
                ),
                decoder=PDPlayableListRep.from_json,
                receive_handlers={
                    E_CATE.REST_SERVER: ProtocolHandler.pd_playable_list_response,
                },
            ),
        )

        # PLAYABLE_LIST_REQ → MESSAGE_BRIDGE / DOWNLOADER
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
                    E_CATE.MESSAGE_BRIDGE: ProtocolHandler.playable_list_request,
                    E_CATE.DOWNLOADER: ProtocolHandler.playable_list_request,
                },
            ),
        )

        # PLAYABLE_LIST_REP → MESSAGE_BRIDGE
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
                    E_CATE.MESSAGE_BRIDGE: ProtocolHandler.playable_list_response,
                },
            ),
        )

        # INR_PLAYABLE_LIST_REQ → DOWNLOADER (Module)
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
                    E_CATE.DOWNLOADER: ProtocolHandler.inr_playable_list_request,
                },
            ),
        )

        # INR_PLAYABLE_LIST_REP → DOWNLOADER (Manager) + group
        cls._register(
            E_PROTOCOL_ID.INR_PLAYABLE_LIST_REP,
            ProtocolEntry(
                factory=lambda sender, receiver, sensor_id, section_list, response: InrPlayableListRep(
                    protocol_id=E_PROTOCOL_ID.INR_PLAYABLE_LIST_REP.value,
                    sender=sender,
                    receiver=receiver,
                    sensor_id=sensor_id,
                    section_list=section_list if section_list is not None else [],
                    response=response,
                ),
                decoder=InrPlayableListRep.from_json,
                receive_handlers={
                    E_CATE.DOWNLOADER: ProtocolHandler.inr_playable_list_response,
                },
                inr_group_receive_handlers={
                    E_CATE.DOWNLOADER: ProtocolHandler.inr_playable_list_response_group,
                },
            ),
        )

        # ===== Play 3계층 =====

        # PD_PLAY_REQ → REST_SERVER
        cls._register(
            E_PROTOCOL_ID.PD_PLAY_REQ,
            ProtocolEntry(
                factory=lambda sender, receiver, section_id, vehicle_id, sensor_id_list, start_time, end_time: PDPlayReq(
                    protocol_id=E_PROTOCOL_ID.PD_PLAY_REQ.value,
                    sender=sender,
                    receiver=receiver,
                    section_id=section_id,
                    vehicle_id=vehicle_id,
                    sensor_id_list=sensor_id_list if sensor_id_list is not None else [],
                    start_time=start_time,
                    end_time=end_time,
                ),
                decoder=PDPlayReq.from_json,
                receive_handlers={
                    E_CATE.REST_SERVER: ProtocolHandler.pd_play_request,
                },
            ),
        )

        # PD_PLAY_REP → REST_SERVER (socket.io broadcast)
        cls._register(
            E_PROTOCOL_ID.PD_PLAY_REP,
            ProtocolEntry(
                factory=lambda sender, receiver, code, code_nm, reason: PDPlayRep(
                    protocol_id=E_PROTOCOL_ID.PD_PLAY_REP.value,
                    sender=sender,
                    receiver=receiver,
                    code=code,
                    code_nm=code_nm,
                    reason=reason,
                ),
                decoder=PDPlayRep.from_json,
                receive_handlers={
                    E_CATE.REST_SERVER: ProtocolHandler.pd_play_response,
                },
            ),
        )

        # PLAY_REQ → BRIDGE / STREAMER / DOWNLOADER (replayer broadcast 패턴)
        cls._register(
            E_PROTOCOL_ID.PLAY_REQ,
            ProtocolEntry(
                factory=lambda sender, receiver, section_id, vehicle_id, sensor_id_list, start_time, end_time: PlayReq(
                    protocol_id=E_PROTOCOL_ID.PLAY_REQ.value,
                    sender=sender,
                    receiver=receiver,
                    section_id=section_id,
                    vehicle_id=vehicle_id,
                    sensor_id_list=sensor_id_list if sensor_id_list is not None else [],
                    start_time=start_time,
                    end_time=end_time,
                ),
                decoder=PlayReq.from_json,
                receive_handlers={
                    E_CATE.MESSAGE_BRIDGE: ProtocolHandler.play_request,
                    E_CATE.STREAMER: ProtocolHandler.play_request,
                    E_CATE.DOWNLOADER: ProtocolHandler.play_request,
                },
            ),
        )

        # PLAY_REP → MESSAGE_BRIDGE
        cls._register(
            E_PROTOCOL_ID.PLAY_REP,
            ProtocolEntry(
                factory=lambda sender, receiver, response=None: PlayRep(
                    protocol_id=E_PROTOCOL_ID.PLAY_REP.value,
                    sender=sender,
                    receiver=receiver,
                    response=response,
                ),
                decoder=PlayRep.from_json,
                receive_handlers={
                    E_CATE.MESSAGE_BRIDGE: ProtocolHandler.play_response,
                },
            ),
        )

        # INR_PLAY_REQ → STREAMER (Module) / DOWNLOADER (Module)
        cls._register(
            E_PROTOCOL_ID.INR_PLAY_REQ,
            ProtocolEntry(
                factory=lambda sender, receiver, section_id, vehicle_id, start_time, end_time: InrPlayReq(
                    protocol_id=E_PROTOCOL_ID.INR_PLAY_REQ.value,
                    sender=sender,
                    receiver=receiver,
                    section_id=section_id,
                    vehicle_id=vehicle_id,
                    start_time=start_time,
                    end_time=end_time,
                ),
                decoder=InrPlayReq.from_json,
                receive_handlers={
                    E_CATE.STREAMER: ProtocolHandler.inr_play_request,
                    E_CATE.DOWNLOADER: ProtocolHandler.inr_play_request,
                },
            ),
        )

        # INR_PLAY_REP → STREAMER (Manager) / DOWNLOADER (Manager) + group
        cls._register(
            E_PROTOCOL_ID.INR_PLAY_REP,
            ProtocolEntry(
                factory=lambda sender, receiver, response=None: InrPlayRep(
                    protocol_id=E_PROTOCOL_ID.INR_PLAY_REP.value,
                    sender=sender,
                    receiver=receiver,
                    response=response,
                ),
                decoder=InrPlayRep.from_json,
                receive_handlers={
                    E_CATE.STREAMER: ProtocolHandler.inr_play_response,
                    E_CATE.DOWNLOADER: ProtocolHandler.inr_play_response,
                },
                inr_group_receive_handlers={
                    E_CATE.STREAMER: ProtocolHandler.inr_play_response_group,
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
    def get_receive_handler(cls, protocol_id: E_PROTOCOL_ID | str, receiver: ReceiverKey) -> HandlerFn:
        cls.initialize()
        pid = cls._to_enum(protocol_id)
        from protocol.protocol_owner import ProtocolOwner
        app_name = ProtocolOwner.get_app_name(receiver) if isinstance(receiver, str) else receiver
        return cls.table[pid].receive_handlers[app_name]

    @classmethod
    def get_inr_group_receive_handler(
        cls, protocol_id: E_PROTOCOL_ID | str, receiver: ReceiverKey
    ) -> GroupHandlerFn | None:
        """매칭되는 group handler가 없으면 None 반환 (기본은 dead — 폴링이 처리)."""
        cls.initialize()
        pid = cls._to_enum(protocol_id)
        return cls.table[pid].inr_group_receive_handlers.get(receiver)

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

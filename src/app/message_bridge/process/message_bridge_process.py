from common.event_bus.stream_bus import StreamBus
from common.process.imdg_bus_process import ImdgBusProcess
from common.process.interfaces import IBusProcess
from protocol.message.packet import E_PROTOCOL_MESSAGE_DIRECTION, IPacket
from protocol.protocol_meta import E_PROTOCOL_ID, ProtocolMeta


class MessageBridgeProcess(ImdgBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        self._stream_bus: StreamBus | None = None

    def on_init(self):
        super().on_init()
        self._stream_bus = StreamBus(self)

    def publish_stream(self, message: str) -> None:
        self._stream_bus.publish(message)

    @staticmethod
    def playable_list_request(process: IBusProcess, packet: IPacket):
        from process_category.enum_category import E_CATE
        from protocol.protocol_owner import ProtocolOwner
        sender = ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE)
        receiver = ProtocolOwner.build(E_CATE.DOWNLOADER, E_CATE.E_DOWNLOADER.E_COMMON.DOWNLOAD_MANAGER)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PLAYABLE_LIST_REQ)
        fwd_packet = factory(
            E_PROTOCOL_MESSAGE_DIRECTION.REQUEST.value,
            sender,
            receiver,
            packet.vehicle_id,
            packet.sensor_id_list,
            packet.start_time,
            packet.end_time,
        )
        process.publish_stream(fwd_packet.to_json())

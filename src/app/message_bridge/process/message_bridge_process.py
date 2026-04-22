from common.event_bus.stream_bus import StreamBus
from common.process.bus_process import BusProcess
from common.process.interfaces import IStreamBusProcess
from protocol.message.packet import E_PROTOCOL_MESSAGE_DIRECTION, Packet
from protocol.protocol_meta import E_PROTOCOL_ID, ProtocolMeta


class MessageBridgeProcess(BusProcess, IStreamBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        self._stream_bus: StreamBus | None = None

    def on_init(self):
        super().on_init()
        self._stream_bus = StreamBus(self)

    def publish_stream(self, message: str) -> None:
        self._stream_bus.publish(message)

    @staticmethod
    def playable_list_request(process: IStreamBusProcess, packet: Packet):
        from process_category.enum_category import E_CATE
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PLAYABLE_LIST_REQ)
        fwd_packet = factory(
            E_PROTOCOL_MESSAGE_DIRECTION.REQUEST.value,
            E_CATE.MESSAGE_BRIDGE,
            E_CATE.DOWNLOADER,
            packet.vehicle_id,
            packet.sensor_id_list,
            packet.start_time,
            packet.end_time,
        )
        process.publish_stream(fwd_packet.to_json())

from common.process.imdg_bus_process import IImdgBusProcess, ImdgBusProcess
from protocol.message.packet import IPacket
from protocol.protocol_meta import E_PROTOCOL_ID, ProtocolMeta


class MessageBridgeProcess(ImdgBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)

    @staticmethod
    def playable_list_request(process: IImdgBusProcess, packet: IPacket):
        from process_category.enum_category import E_CATE
        from protocol.protocol_owner import ProtocolOwner
        sender = ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE)
        receiver = ProtocolOwner.build(E_CATE.DOWNLOADER, E_CATE.E_DOWNLOADER.E_COMMON.DOWNLOAD_MANAGER)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PLAYABLE_LIST_REQ)
        fwd_packet = factory(
            sender,
            receiver,
            packet.vehicle_id,
            packet.sensor_id_list,
            packet.start_time,
            packet.end_time,
        )
        process.send_message_imdg(fwd_packet.to_json())

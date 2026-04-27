from common.process.imdg_bus_process import IImdgBusProcess, ImdgBusProcess
from protocol.message.message import IMessage
from protocol.protocol_meta import E_PROTOCOL_ID, ProtocolMeta
from protocol.protocol_wrapper import ProtocolWrapper


class MessageBridgeProcess(ImdgBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)

    @staticmethod
    def playable_list_request(process: IImdgBusProcess, wrapper: ProtocolWrapper, packet: IMessage):
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
        envelope = ProtocolWrapper.get_protocol_wrapper(fwd_packet).get_protocol_packet_message()
        process.send_message_imdg(envelope)

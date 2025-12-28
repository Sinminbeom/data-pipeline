import json
from abc import abstractmethod
from flask_socketio import SocketIO
from flask import Flask

from src.common.process.bus_process import BusProcess
from src.common.process.queue_control_process import QueueControlProcess
from src.protocol.message.external.ui.playable_list import PDPlayableListReq
from src.protocol.message.packet import E_PROTOCOL_MESSAGE_DIRECTION
from src.protocol.protocol_meta import ProtocolMeta, E_PROTOCOL_ID
from src.protocol.protocol_wrapper import ProtocolWrapper


class abWebSocketServer:

    def __init__(self, _parents_process: QueueControlProcess, _bind_ip='0.0.0.0', _port=9999):
        print("11111111111111111111111111111111")
        self.parents_process: QueueControlProcess = _parents_process
        print("22222222222222222222222222222222222")

        print("33333333333333333333333333333333333")
        self.socket_io_app = Flask(__name__)
        print("4444444444444444444444444444444444444")
        self.socket_io_app.secret_key = "mysecret"

        print("55555555555555555555555555555555")

        self.bindIP = _bind_ip
        self.port = _port

        print("6666666666666666666666666666666666666")
        self.socketIO = SocketIO(self.socket_io_app)
        print("777777777777777777777777777777777")

        self.init()

    def init(self):
        self.on_init()
        pass

    def start(self):
        # self.socketIO.run(self.socket_io_app, debug=False, port=9999, allow_unsafe_werkzeug=True)
        self.socketIO.run(self.socket_io_app, debug=False, host=self.bindIP, port=self.port, allow_unsafe_werkzeug=True)

    def __get_app(self):
        return self.socket_io_app

    @abstractmethod
    def on_init(self):
        pass

    def get_parent_process(self) -> QueueControlProcess:
        return self.parents_process


class SocketIOServer(abWebSocketServer):

    def __init__(self, _parents_process, _bind_ip, _bind_port):
        abWebSocketServer.__init__(self, _parents_process, _bind_ip, _bind_port)

    @staticmethod
    def playable_list_request(process: BusProcess, protocol_wrapper: ProtocolWrapper, protocol_message: PDPlayableListReq):
        from src.process_category.enum_category import E_CATE
        print("Call Back  PlayableListRequest")

        sender = E_CATE.REST_SERVER
        receiver = E_CATE.MESSAGE_BRIDGE

        message = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PLAYABLE_LIST_REQ)(
            E_PROTOCOL_MESSAGE_DIRECTION.REQUEST, sender, receiver,
            protocol_message.vehicle_id,
            protocol_message.sensor_id_list,
            protocol_message.start_time, protocol_message.end_time
        )

        packet_message = ProtocolMeta.get_protocol_packet_message(message)
        process.send_message_imdg(packet_message)

    def on_init(self):
        super().on_init()
        self.get_parent_process().on_register_handler(ProtocolMeta.get_receive_handler_container())

        @self.socket_io_app.route('/')
        def hello_world():
            return "Hello Project Home Page!!"

        @self.socketIO.on("message")
        def request(message):
            print("message : " + message)

            parsed_dict = json.loads(message)

            protocol_id = parsed_dict["protocol_id"]
            receiver_name = parsed_dict["receiver"]

            if receiver_name != self.get_parent_process().get_app_name():
                print("Rest Server Recv Packet MissMatch!!")
                return

            message_object = ProtocolMeta.get_json_decoder(protocol_id)(message)

            print(message_object)

            protocol_wrapper = ProtocolWrapper.get_protocol_wrapper(message_object)

            recv_handler = ProtocolMeta.get_receive_handler(protocol_id, receiver_name)
            recv_handler(self.get_parent_process(), protocol_wrapper, message_object)

        pass
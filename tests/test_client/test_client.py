import socketio

def test_client():

    sio = socketio.Client()

    @sio.event
    def connect():
        print("Connected to the server")

    @sio.event
    def disconnect():
        print("Disconnected from the server")

    def send_message_to_server(message):
        sio.emit('message', message)

    sio.connect('http://localhost:9999')

    send_message_to_server("""{"protocol_id": "PD_100", "message_direction": 1, "sender": "UI", "receiver": "REST_SERVER", "vehicle_id": "e-100", "sensor_id_list": ["LIDAR"], "start_time": "20230602000000", "end_time": "20230602000115"}""")

    sio.wait()
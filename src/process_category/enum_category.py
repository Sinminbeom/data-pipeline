from define.enum import IENUM

from src.app.downloader.process.downloader_manager import DownloaderManager
from src.app.downloader.process.downloader_module import DownloaderModule
from src.app.message_bridge.process.message_bridge_process import MessageBridgeProcess
from src.app.rest.process.socketio_process import SocketIOProcess
from src.process_category.enum_sensor import E_LIDAR, E_CAMERA


class E_CATE_META_ELE(IENUM):
    NAME = 0
    LAMBDA = 1


class E_CATE(IENUM):
    MESSAGE_BRIDGE="MESSAGE_BRIDGE"
    DOWNLOADER = "DOWNLOADER"
    REST_SERVER = "REST_SERVER"

    class E_MESSAGE_BRIDGE(IENUM):
        COMMON = "COMMON"
        class E_COMMON(IENUM):
            MESSAGE_BRIDGE = "MESSAGE_BRIDGE"
            E_MESSAGE_BRIDGE = (MESSAGE_BRIDGE, lambda _app_name, _process_name: MessageBridgeProcess(_app_name,_process_name))

    class E_DOWNLOADER(IENUM):
        COMMON = "COMMON"
        LIDAR = "LIDAR"
        GNSS = "GNSS"
        CAMERA = "CAMERA"

        class E_COMMON(IENUM):
            DOWNLOAD_MANAGER = "DOWNLOAD_MANAGER"
            E_DOWNLOAD_MANAGER = (DOWNLOAD_MANAGER, lambda _app_name, _process_name: DownloaderManager(_app_name, _process_name))

        class E_LIDAR(IENUM):
            AT128_ROOF_FRONT = E_LIDAR.AT128_ROOF_FRONT ## "AT128_ROOF_FRONT"
            E_AT128_ROOF_FRONT = (AT128_ROOF_FRONT, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))
            AT128_ROOF_RIGHT = E_LIDAR.AT128_ROOF_RIGHT ## "AT128_ROOF_RIGHT"
            E_AT128_ROOF_RIGHT = (AT128_ROOF_RIGHT, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))
            AT128_ROOF_REAR = E_LIDAR.AT128_ROOF_REAR ## "AT128_ROOF_REAR"
            E_AT128_ROOF_REAR = (AT128_ROOF_REAR, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))
            AT128_ROOF_LEFT = E_LIDAR.AT128_ROOF_LEFT ## "AT128_ROOF_LEFT"
            E_AT128_ROOF_LEFT = (AT128_ROOF_LEFT, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))

            RSBP_BUMP_FRONT = E_LIDAR.RSBP_BUMP_FRONT ## "RSBP_BUMP_FRONT"
            E_RSBP_BUMP_FRONT = (RSBP_BUMP_FRONT, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))
            RSBP_BUMP_RIGHT = E_LIDAR.RSBP_BUMP_RIGHT ## "RSBP_BUMP_RIGHT"
            E_RSBP_BUMP_RIGHT = (RSBP_BUMP_RIGHT, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))
            RSBP_BUMP_REAR = E_LIDAR.RSBP_BUMP_REAR  ## "RSBP_BUMP_REAR"
            E_RSBP_BUMP_REAR = (RSBP_BUMP_REAR, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))
            RSBP_BUMP_LEFT = E_LIDAR.RSBP_BUMP_LEFT ## "RSBP_BUMP_LEFT"
            E_RSBP_BUMP_LEFT = (RSBP_BUMP_LEFT, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))

        class E_GNSS(IENUM):
            GNSS = "GNSS"
            E_GNSS = (GNSS, lambda _app_name, _process_name: DownloaderModule(_app_name, _process_name))

        class E_CAMERA(IENUM):
            AM20_FRONT_CENTER_RIGHT_DOWN = E_CAMERA.AM20_FRONT_CENTER_RIGHT_DOWN ## "AM20_FRONT_CENTER_RIGHT_DOWN"
            E_AM20_FRONT_CENTER_RIGHT_DOWN = (
                AM20_FRONT_CENTER_RIGHT_DOWN, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))
            AM20_FRONT_RIGHT_REAR =  E_CAMERA.AM20_FRONT_RIGHT_REAR ##  "AM20_FRONT_RIGHT_REAR"
            E_AM20_FRONT_RIGHT_REAR = (
                AM20_FRONT_RIGHT_REAR, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))
            AM20_REAR_CENTER_RIGHT = E_CAMERA.AM20_REAR_CENTER_RIGHT ##  "AM20_REAR_CENTER_RIGHT"
            E_AM20_REAR_CENTER_RIGHT = (
                AM20_REAR_CENTER_RIGHT, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))
            AM20_FRONT_LEFT_REAR = E_CAMERA.AM20_FRONT_LEFT_REAR ##  "AM20_FRONT_LEFT_REAR"
            E_AM20_FRONT_LEFT_REAR = (
                AM20_FRONT_LEFT_REAR, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))
            AM20_REAR_RIGHT_EDGE = E_CAMERA.AM20_REAR_RIGHT_EDGE ## "AM20_REAR_RIGHT_EDGE"
            E_AM20_REAR_RIGHT_EDGE = (
                AM20_REAR_RIGHT_EDGE, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))

            AM20_LEFT_REAR_EDGE = E_CAMERA.AM20_LEFT_REAR_EDGE ## "AM20_LEFT_REAR_EDGE"
            E_AM20_LEFT_REAR_EDGE = (AM20_LEFT_REAR_EDGE, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))
            AM20_FRONT_CENTER_LEFT_UP = E_CAMERA.AM20_FRONT_CENTER_LEFT_UP ## "AM20_FRONT_CENTER_LEFT_UP"
            E_AM20_FRONT_CENTER_LEFT_UP = (
                AM20_FRONT_CENTER_LEFT_UP, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))
            AM20_FRONT_CENTER_RIGHT_UP = E_CAMERA.AM20_FRONT_CENTER_RIGHT_UP ## "AM20_FRONT_CENTER_RIGHT_UP"
            E_AM20_FRONT_CENTER_RIGHT_UP = (
                AM20_FRONT_CENTER_RIGHT_UP, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))
            AM20_FRONT_RIGHT_FRONT = E_CAMERA.AM20_FRONT_RIGHT_FRONT ## "AM20_FRONT_RIGHT_FRONT"
            E_AM20_FRONT_RIGHT_FRONT = (
                AM20_FRONT_RIGHT_FRONT, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))
            AM20_FRONT_LEFT_FRONT = E_CAMERA.AM20_FRONT_LEFT_FRONT ##  "AM20_FRONT_LEFT_FRONT"
            E_AM20_FRONT_LEFT_FRONT = (
                AM20_FRONT_LEFT_FRONT, lambda _app_name,_process_name: DownloaderModule(_app_name, _process_name))

    class E_REST_SERVER(IENUM):
        COMMON = "COMMON"
        class E_COMMON(IENUM):
            REST_SERVER = "REST_SERVER"
            E_REST_SERVER = (REST_SERVER, lambda _app_name, _process_name: SocketIOProcess(_app_name,_process_name))


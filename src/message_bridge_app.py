import time

from logger.app_logger import AppLogger

from src.app.app_object import MultiProcessManagerAppFromCate
from src.config.project_config import ProjectConfig
from src.process_category.enum_category import E_CATE
from src.process_category.process_category import ProcessCategory


class MessageBridge(MultiProcessManagerAppFromCate):

    def __init__(self, *_cate):
        super().__init__(E_CATE.MESSAGE_BRIDGE, *_cate)
        pass

    def init(self):
        self.get_multi_process_manager().start()

    def on_run(self):
        time.sleep(0.1)
        pass


def main():
    try:
        AppLogger.set_config("../conf/logging.conf", "message-bridge")
        ProjectConfig.set_config("../conf/application_windows.conf")
        ProcessCategory.instance().register_message_bridge()

        app = MessageBridge(E_CATE.MESSAGE_BRIDGE)
        app.init()
        app.run()

    except Exception as e:
        AppLogger.instance().error("Message Bridge Not Launched")
        raise e



if __name__ == '__main__':
    main()

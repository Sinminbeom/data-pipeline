import time

from logger.app_logger import AppLogger

from src.app.app_object import MultiProcessManagerAppFromCate
from src.process_category.enum_category import E_CATE
from src.process_category.process_category import ProcessCategory


class RestServer(MultiProcessManagerAppFromCate):
    def __init__(self, *_cate):
        super().__init__(E_CATE.REST_SERVER, *_cate)

    def init(self):
        self.get_multi_process_manager().start()

    def on_run(self):
        time.sleep(0.1)
        pass


def main():
    try:
        AppLogger.set_config("../conf/logging.conf", "rest-server")
        ProcessCategory.instance().register_rest_server()

        app = RestServer(E_CATE.REST_SERVER)
        app.init()
        app.run()
    except Exception as e:
        AppLogger.instance().error("Rest Server Not Launched")
        raise e


if __name__ == '__main__':
    main()
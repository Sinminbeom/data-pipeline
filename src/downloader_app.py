import time

from python_library.logger.app_logger import AppLogger

from app.app_object import MultiProcessManagerAppFromCate
from config.project_config import ProjectConfig
from process_category.enum_category import E_CATE
from process_category.process_category import ProcessCategory


class Downloader(MultiProcessManagerAppFromCate):

    def __init__(self, *_cate):
        super().__init__(E_CATE.DOWNLOADER, *_cate)

    def init(self):
        self.get_multi_process_manager().start()

    def on_run(self):
        time.sleep(0.005)
        pass




def main():
    try:
        AppLogger.set_config("./conf/logging.conf", "downloader")
        ProjectConfig.set_config("./conf/application.conf")
        ProcessCategory.instance().register_downloader()

        app = Downloader(E_CATE.DOWNLOADER)
        app.init()
        app.run()

    except Exception as e:
        AppLogger.instance().error("Downloader Not Launched")
        raise e


if __name__ == '__main__':
    main()

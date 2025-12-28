import time

from logger.app_logger import AppLogger

from src.app.app_object import MultiProcessManagerAppFromCate
from src.config.project_config import ProjectConfig
from src.process_category.enum_category import E_CATE
from src.process_category.process_category import ProcessCategory


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
        AppLogger.set_config("../conf/logging.conf", "downloader")
        ProjectConfig.set_config("../conf/application_windows.conf")
        ProcessCategory.instance().register_downloader()

        app = Downloader(E_CATE.DOWNLOADER)
        app.init()
        app.run()

    except Exception as e:
        AppLogger.instance().error("Downloader Not Launched")
        raise e


if __name__ == '__main__':
    main()

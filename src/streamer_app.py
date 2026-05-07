import time

from app.app_object import MultiProcessManagerAppFromCate
from process_category.enum_category import E_CATE
from process_category.process_category import ProcessCategory
from config.project_config import ProjectConfig


class Streamer(MultiProcessManagerAppFromCate):

    def __init__(self, *_cate):
        super().__init__(E_CATE.STREAMER, *_cate)

    def init(self):
        self.get_multi_process_manager().start()

    def on_run(self):
        time.sleep(0.005)
        pass


def main():
    ProjectConfig.set_config(ProjectConfig.DEFAULT_CONFIG_PATH)

    ProcessCategory.instance().register_streamer()

    app = Streamer(E_CATE.STREAMER)
    app.init()
    app.run()


if __name__ == '__main__':
    main()

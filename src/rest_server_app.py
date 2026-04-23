import time

from app.app_object import MultiProcessManagerAppFromCate
from process_category.enum_category import E_CATE
from process_category.process_category import ProcessCategory
from config.project_config import ProjectConfig


class RestServer(MultiProcessManagerAppFromCate):
    def __init__(self, *_cate):
        super().__init__(E_CATE.REST_SERVER, *_cate)

    def init(self):
        self.get_multi_process_manager().start()

    def on_run(self):
        time.sleep(0.1)
        pass


def main():
    ProjectConfig.set_config(ProjectConfig.DEFAULT_CONFIG_PATH)

    ProcessCategory.instance().register_rest_server()

    app = RestServer(E_CATE.REST_SERVER)
    app.init()
    app.run()


if __name__ == '__main__':
    main()

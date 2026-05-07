from python_library.configure.app_config import AppConfig
from python_library.define.enum import IENUM


class ProjectConfig(AppConfig):
    DEFAULT_CONFIG_PATH = "./conf/application.conf"
    DEFAULT_LOGGING_CONFIG_PATH = "./conf/logging.conf"

    class E_CATE_TYPE(IENUM):
        COMMON = "COOMON"
        IMDG = "IMDG"
        REST = "REST"
        STREAM = "STREAM"
        STORAGE = "STORAGE"

    class E_CATE_ELE_COMMON(IENUM):
        PROJECT_NAME = "PROJECT_NAME"
        CHANNEL_NAME = "CHANNEL_NAME"
        pass

    class E_CATE_ELE_IMDG(IENUM):
        SERVER_IP = "SERVER_IP"
        SERVER_PORT = "SERVER_PORT"
        POOL_SIZE = "POOL_SIZE"
        SCHEMA_NAME = "SCHEMA_NAME"
        pass

    class E_CATE_ELE_REST(IENUM):
        BIND_IP = "BIND_IP"
        BIND_PORT = "BIND_PORT"
        pass

    class E_CATE_ELE_STREAM(IENUM):
        STREAM_NAME = "STREAM_NAME"
        GROUP_NAME = "GROUP_NAME"
        pass

    class E_CATE_ELE_STORAGE(IENUM):
        ROOT = "ROOT"
        PREFIX = "PREFIX"
        pass

    def __init__(self) -> None:
        super().__init__()

        self.project_name = self.get_config(
            ProjectConfig.E_CATE_TYPE.COMMON, ProjectConfig.E_CATE_ELE_COMMON.PROJECT_NAME
        )
        self.channel_name = self.get_config(
            ProjectConfig.E_CATE_TYPE.COMMON, ProjectConfig.E_CATE_ELE_COMMON.CHANNEL_NAME
        )

        self.server_ip = self.get_config(
            ProjectConfig.E_CATE_TYPE.IMDG, ProjectConfig.E_CATE_ELE_IMDG.SERVER_IP
        )
        self.server_port = self.get_config(
            ProjectConfig.E_CATE_TYPE.IMDG, ProjectConfig.E_CATE_ELE_IMDG.SERVER_PORT
        )
        self.pool_size = self.get_config(
            ProjectConfig.E_CATE_TYPE.IMDG, ProjectConfig.E_CATE_ELE_IMDG.POOL_SIZE
        )
        self.schema_name = self.get_config(
            ProjectConfig.E_CATE_TYPE.IMDG, ProjectConfig.E_CATE_ELE_IMDG.SCHEMA_NAME
        )

        self.bind_ip = self.get_config(
            ProjectConfig.E_CATE_TYPE.REST, ProjectConfig.E_CATE_ELE_REST.BIND_IP
        )
        self.bind_port = int(self.get_config(
            ProjectConfig.E_CATE_TYPE.REST, ProjectConfig.E_CATE_ELE_REST.BIND_PORT
        ))

        self.stream_name = self.get_config(
            ProjectConfig.E_CATE_TYPE.STREAM, ProjectConfig.E_CATE_ELE_STREAM.STREAM_NAME
        )
        self.stream_group_name = self.get_config(
            ProjectConfig.E_CATE_TYPE.STREAM, ProjectConfig.E_CATE_ELE_STREAM.GROUP_NAME
        )

        self.storage_root = self.get_config(
            ProjectConfig.E_CATE_TYPE.STORAGE, ProjectConfig.E_CATE_ELE_STORAGE.ROOT
        )
        self.storage_prefix = self.get_config(
            ProjectConfig.E_CATE_TYPE.STORAGE, ProjectConfig.E_CATE_ELE_STORAGE.PREFIX
        )
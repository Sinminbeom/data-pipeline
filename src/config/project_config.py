from configure.app_config import AppConfig
from define.enum import IENUM


class ProjectConfig(AppConfig):
    class E_CATE_TYPE(IENUM):
        COMMON = "COOMON"
        IMDG = "IMDG"
        REST = "REST"

    class E_CATE_ELE_COMMON(IENUM):
        PROJECT_NAME = "ProjectName"
        CHANNEL_NAME = "ChannelName"
        pass

    class E_CATE_ELE_IMDG(IENUM):
        SERVER_IP = "ServerIp"
        SERVER_PORT = "ServerPort"
        POOL_SIZE = "PoolSize"
        SCHEMA_NAME = "SchemaName"
        pass

    class E_CATE_ELE_REST(IENUM):
        BIND_IP = "BindIp"
        BIND_PORT = "BindPort"
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
from typing import List, Any, Tuple, Iterable

from category.app_category import AppCategory
from category.category_action import CategoryAction
from category.category_group import CategoryGroup

from src.process_category.enum_category import E_CATE, E_CATE_META_ELE


class ProcessCategory(AppCategory):
    def __init__(self) -> None:
        super().__init__()

    def register_category(self) -> None:
        self.cate_reg_queue[E_CATE.MESSAGE_BRIDGE] = lambda: self.register_message_bridge()
        self.cate_reg_queue[E_CATE.DOWNLOADER] = lambda: self.register_downloader()
        self.cate_reg_queue[E_CATE.REST_SERVER] = lambda: self.register_rest_server()

    def register_message_bridge(self) -> None:
        message_bridge = CategoryGroup()
        common = CategoryGroup()

        common.push(
            E_CATE.E_MESSAGE_BRIDGE.E_COMMON.E_MESSAGE_BRIDGE[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_MESSAGE_BRIDGE.E_COMMON.E_MESSAGE_BRIDGE[E_CATE_META_ELE.LAMBDA]),
        )

        message_bridge.push(E_CATE.E_MESSAGE_BRIDGE.COMMON, common)
        self.cate_queue[E_CATE.MESSAGE_BRIDGE] = message_bridge

    def register_downloader(self) -> None:
        """
        cProcessCate.RegisterDownloader()와 동일한 구성을 CategoryGroup 트리로 구성
        구조:
          cate_queue[DOWNLOADER]
            ├─ COMMON : { <name> : action }
            ├─ LIDAR  : { <name> : action, ... }
            ├─ GNSS   : { <name> : action }
            └─ CAMERA : { <name> : action, ... }
        """
        downloader = CategoryGroup()

        common = CategoryGroup()
        lidar = CategoryGroup()
        gnss = CategoryGroup()
        camera = CategoryGroup()

        # --- COMMON ---
        common.push(
            E_CATE.E_DOWNLOADER.E_COMMON.E_DOWNLOAD_MANAGER[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_COMMON.E_DOWNLOAD_MANAGER[E_CATE_META_ELE.LAMBDA]),
        )

        # --- LIDAR : AT128 ROOF (FRONT/RIGHT/REAR/LEFT) ---
        lidar.push(
            E_CATE.E_DOWNLOADER.E_LIDAR.E_AT128_ROOF_FRONT[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_LIDAR.E_AT128_ROOF_FRONT[E_CATE_META_ELE.LAMBDA]),
        )
        lidar.push(
            E_CATE.E_DOWNLOADER.E_LIDAR.E_AT128_ROOF_RIGHT[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_LIDAR.E_AT128_ROOF_RIGHT[E_CATE_META_ELE.LAMBDA]),
        )
        lidar.push(
            E_CATE.E_DOWNLOADER.E_LIDAR.E_AT128_ROOF_REAR[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_LIDAR.E_AT128_ROOF_REAR[E_CATE_META_ELE.LAMBDA]),
        )
        lidar.push(
            E_CATE.E_DOWNLOADER.E_LIDAR.E_AT128_ROOF_LEFT[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_LIDAR.E_AT128_ROOF_LEFT[E_CATE_META_ELE.LAMBDA]),
        )

        # --- LIDAR : RSBP BUMP (FRONT/RIGHT/REAR/LEFT) ---
        lidar.push(
            E_CATE.E_DOWNLOADER.E_LIDAR.E_RSBP_BUMP_FRONT[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_LIDAR.E_RSBP_BUMP_FRONT[E_CATE_META_ELE.LAMBDA]),
        )
        lidar.push(
            E_CATE.E_DOWNLOADER.E_LIDAR.E_RSBP_BUMP_RIGHT[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_LIDAR.E_RSBP_BUMP_RIGHT[E_CATE_META_ELE.LAMBDA]),
        )
        lidar.push(
            E_CATE.E_DOWNLOADER.E_LIDAR.E_RSBP_BUMP_REAR[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_LIDAR.E_RSBP_BUMP_REAR[E_CATE_META_ELE.LAMBDA]),
        )
        lidar.push(
            E_CATE.E_DOWNLOADER.E_LIDAR.E_RSBP_BUMP_LEFT[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_LIDAR.E_RSBP_BUMP_LEFT[E_CATE_META_ELE.LAMBDA]),
        )

        # --- GNSS ---
        gnss.push(
            E_CATE.E_DOWNLOADER.E_GNSS.E_GNSS[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_GNSS.E_GNSS[E_CATE_META_ELE.LAMBDA]),
        )

        # --- CAMERA : AM20 ---
        camera.push(
            E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_FRONT_CENTER_RIGHT_DOWN[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_FRONT_CENTER_RIGHT_DOWN[E_CATE_META_ELE.LAMBDA]),
        )
        camera.push(
            E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_FRONT_RIGHT_REAR[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_FRONT_RIGHT_REAR[E_CATE_META_ELE.LAMBDA]),
        )
        camera.push(
            E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_REAR_CENTER_RIGHT[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_REAR_CENTER_RIGHT[E_CATE_META_ELE.LAMBDA]),
        )
        camera.push(
            E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_FRONT_LEFT_REAR[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_FRONT_LEFT_REAR[E_CATE_META_ELE.LAMBDA]),
        )
        camera.push(
            E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_REAR_RIGHT_EDGE[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_REAR_RIGHT_EDGE[E_CATE_META_ELE.LAMBDA]),
        )
        camera.push(
            E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_LEFT_REAR_EDGE[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_LEFT_REAR_EDGE[E_CATE_META_ELE.LAMBDA]),
        )
        camera.push(
            E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_FRONT_CENTER_LEFT_UP[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_FRONT_CENTER_LEFT_UP[E_CATE_META_ELE.LAMBDA]),
        )
        camera.push(
            E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_FRONT_CENTER_RIGHT_UP[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_FRONT_CENTER_RIGHT_UP[E_CATE_META_ELE.LAMBDA]),
        )
        camera.push(
            E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_FRONT_RIGHT_FRONT[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_FRONT_RIGHT_FRONT[E_CATE_META_ELE.LAMBDA]),
        )
        camera.push(
            E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_FRONT_LEFT_FRONT[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_DOWNLOADER.E_CAMERA.E_AM20_FRONT_LEFT_FRONT[E_CATE_META_ELE.LAMBDA]),
        )

        # cate2 그룹을 cate1(DOWNLOADER) 하위에 붙이기
        downloader.push(E_CATE.E_DOWNLOADER.COMMON, common)
        downloader.push(E_CATE.E_DOWNLOADER.LIDAR, lidar)
        downloader.push(E_CATE.E_DOWNLOADER.GNSS, gnss)
        downloader.push(E_CATE.E_DOWNLOADER.CAMERA, camera)

        self.cate_queue[E_CATE.DOWNLOADER] = downloader

    def register_rest_server(self) -> None:
        rest_server = CategoryGroup()
        common = CategoryGroup()

        common.push(
            E_CATE.E_REST_SERVER.E_COMMON.E_REST_SERVER[E_CATE_META_ELE.NAME],
            CategoryAction(E_CATE.E_REST_SERVER.E_COMMON.E_REST_SERVER[E_CATE_META_ELE.LAMBDA]),
        )

        rest_server.push(E_CATE.E_REST_SERVER.COMMON, common)
        self.cate_queue[E_CATE.REST_SERVER] = rest_server

    def get_process_list_category(self, *_cate) -> List[Tuple[Any, Any]]:
        """
        legacy cProcessCate.GetProcessListsCate 와 동일한 역할.
        반환: [(cate3_name, CategoryAction), ...]
        """
        def _items(group: Any) -> Iterable[Tuple[Any, Any]]:
            # CategoryGroup이 dict처럼 items()를 제공한다고 가정하되,
            # 내부 구현이 다를 수 있으니 최대한 안전하게 처리
            if group is None:
                return []
            if hasattr(group, "items") and callable(getattr(group, "items")):
                return group.items()
            if hasattr(group, "queue"):
                return group.queue.items()
            if hasattr(group, "_queue"):
                return group._queue.items()
            if isinstance(group, dict):
                return group.items()
            raise TypeError(f"Unsupported group type: {type(group)}")

        def _get(group: Any, key: Any) -> Any:
            if group is None:
                return None
            if hasattr(group, "get") and callable(getattr(group, "get")):
                return group.get(key)
            if hasattr(group, "queue"):
                return group.queue.get(key)
            if hasattr(group, "_queue"):
                return group._queue.get(key)
            if isinstance(group, dict):
                return group.get(key)
            return None

        if len(_cate) not in (1, 2, 3):
            raise ValueError("get_process_list_category expects 1~3 category keys")

        cate1 = _cate[0]
        cate1_group = self.cate_queue.get(cate1)
        if cate1_group is None:
            return []

        # depth=1 : cate1 하위 모든 cate2를 펼쳐서 leaf 반환
        if len(_cate) == 1:

            ret: List[Tuple[Any, Any]] = []
            for _, cate2_group in _items(cate1_group):
                # cate2_group 안에는 (cate3_name -> CategoryAction) leaf가 들어있음
                for k, v in _items(cate2_group):
                    ret.append((k, v))
            return ret

        # depth=2 : cate1/cate2 하위 leaf 반환
        cate2 = _cate[1]
        cate2_group = _get(cate1_group, cate2)
        if cate2_group is None:
            return []

        if len(_cate) == 2:
            return [(k, v) for k, v in _items(cate2_group)]

        # depth=3 : cate1/cate2/cate3 하나 반환
        cate3 = _cate[2]
        leaf = _get(cate2_group, cate3)
        if leaf is None:
            return []
        return [(cate3, leaf)]

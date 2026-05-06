from sensor_category.enum_sensor import E_CAMERA, E_GNSS, E_LIDAR, E_SENSOR_TYPE


class SensorCategory:
    """센서 ID ↔ 카테고리 매핑 정적 레지스트리.

    스토리지 경로 구성 시 sensor_id로부터 category("lidar"/"gnss"/"camera")를
    얻어내기 위한 lookup 클래스. E_LIDAR/E_GNSS/E_CAMERA 클래스의 멤버를
    introspection으로 훑어서 매핑 테이블을 자동 구성하므로, 새 센서를 enum에
    추가하면 이 클래스도 자동 반영된다 (별도 등록 코드 불필요).

    매핑 결과 예시:
        AT128_ROOF_FRONT             → "lidar"
        GNSS                         → "gnss"
        AM20_FRONT_CENTER_RIGHT_DOWN → "camera"

    경로 구성 예시:
        {root}/{prefix}/{vehicle_id}/{category}/{sensor_id_lower}/...
                                     └─ SensorCategory.get(sensor_id) 결과
    """

    @staticmethod
    def _build_map() -> dict[str, str]:
        """E_LIDAR/E_GNSS/E_CAMERA 클래스 멤버를 훑어 sensor_id → category dict 구성."""
        result: dict[str, str] = {}
        for cls, category in (
            (E_LIDAR, E_SENSOR_TYPE.LIDAR.lower()),
            (E_GNSS, E_SENSOR_TYPE.GNSS.lower()),
            (E_CAMERA, E_SENSOR_TYPE.CAMERA.lower()),
        ):
            for name, value in vars(cls).items():
                # private/dunder 어트리뷰트와 string이 아닌 값(메서드 등) 제외
                if name.startswith("_") or not isinstance(value, str):
                    continue
                result[value] = category
        return result

    # 클래스 정의 시점에 한 번만 실행되어 immutable한 lookup 테이블이 됨
    _BY_SENSOR_ID: dict[str, str] = _build_map()

    @classmethod
    def get(cls, sensor_id: str) -> str | None:
        """sensor_id에 대응되는 category 반환. 미등록 sensor_id는 None."""
        return cls._BY_SENSOR_ID.get(sensor_id)

    @classmethod
    def has(cls, sensor_id: str) -> bool:
        """sensor_id가 등록되어 있는지 여부."""
        return sensor_id in cls._BY_SENSOR_ID

    @classmethod
    def all_sensor_ids(cls) -> list[str]:
        """등록된 모든 sensor_id를 알파벳 순으로 반환."""
        return sorted(cls._BY_SENSOR_ID.keys())

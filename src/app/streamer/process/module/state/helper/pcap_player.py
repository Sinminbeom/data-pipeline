from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional

from pcaps.packet import PcapPacket
from pcaps.pool import PcapPool
from pcaps.reader.multi import MultiPcapReader
from sensor_category.sensor_category import SensorCategory

_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"
_DATE_FORMAT = "%Y%m%d"
_HOUR_FORMAT = "%H"
_MINUTE_FORMAT = "%M"


class PcapPlayer:
    """sensor 1개에 대한 1초 단위 PCAP 파일 read 흐름.

    storage path 구성:
        {storage_root}/{storage_prefix}/{vehicle}/{category}/{sensor_lower}/
            {YYYYMMDD}/{HH}/{MM}/{sensor_lower}_{YYYYMMDDHH24MISS}.pcap

    sender thread 통합은 Phase 2 — 본 helper는 read만 담당.
    """

    def __init__(
        self,
        storage_root: str,
        storage_prefix: str,
        vehicle_id: str,
        sensor_id: str,
        start_time: str,
        end_time: str,
    ) -> None:
        self._storage_root = storage_root
        self._storage_prefix = storage_prefix
        self._vehicle_id = vehicle_id
        self._sensor_id = sensor_id
        self._start_time = start_time
        self._end_time = end_time

        self._pool: PcapPool = PcapPool()
        self._error: Optional[Exception] = None

    def read(self) -> bool:
        """1초 단위로 PCAP 파일을 순차 read하여 PcapPool에 누적. 성공 True."""
        try:
            category = SensorCategory.get(self._sensor_id)
            if category is None:
                self._error = ValueError(f"unknown sensor: {self._sensor_id}")
                return False

            multi_reader = MultiPcapReader()
            start_dt = datetime.strptime(self._start_time, _TIMESTAMP_FORMAT)
            end_dt = datetime.strptime(self._end_time, _TIMESTAMP_FORMAT)

            cursor = start_dt
            while cursor < end_dt:
                file_path = self._build_pcap_path(category, cursor)
                if not os.path.isfile(file_path):
                    self._error = FileNotFoundError(file_path)
                    return False

                reader = multi_reader.read(file_path)
                for packet in reader.pool.packets:
                    self._pool.append(packet)

                cursor += timedelta(seconds=1)

            return True
        except Exception as exc:
            self._error = exc
            return False

    @property
    def pool(self) -> PcapPool:
        return self._pool

    @property
    def error(self) -> Optional[Exception]:
        return self._error

    @property
    def packet_count(self) -> int:
        return self._pool.size

    def _build_pcap_path(self, category: str, when: datetime) -> str:
        sensor_lower = self._sensor_id.lower()
        timestamp = when.strftime(_TIMESTAMP_FORMAT)
        parts = [
            self._storage_root,
            self._storage_prefix,
            self._vehicle_id,
            category,
            sensor_lower,
            when.strftime(_DATE_FORMAT),
            when.strftime(_HOUR_FORMAT),
            when.strftime(_MINUTE_FORMAT),
            f"{sensor_lower}_{timestamp}.pcap",
        ]
        joined = "/".join(p for p in parts if p)
        return os.path.normpath(joined)

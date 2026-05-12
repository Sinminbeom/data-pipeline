from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
from typing import Callable, Optional

from python_library.thread.thread import abThread

from pcaps.pool import PcapPool
from pcaps.reader.multi import MultiPcapReader
from sensor_category.sensor_category import SensorCategory

_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"
_DATE_FORMAT = "%Y%m%d"
_HOUR_FORMAT = "%H"
_MINUTE_FORMAT = "%M"

ReadyCallback = Callable[[float], None]
ErrorCallback = Callable[[Exception], None]


class PcapReaderThread(abThread):
    """sensor 1개에 대한 1초 단위 PCAP 파일 read producer thread.

    buffer가 가득 차면 wait, ready_threshold만큼 읽으면 ready_callback 호출.
    """

    def __init__(
        self,
        pool: PcapPool,
        storage_root: str,
        storage_prefix: str,
        vehicle_id: str,
        sensor_id: str,
        start_time: str,
        end_time: str,
        ready_threshold_seconds: int = 2,
        file_refind_count: int = 3,
        file_refind_sleep_time: float = 0.1,
        on_ready: Optional[ReadyCallback] = None,
        on_error: Optional[ErrorCallback] = None,
    ) -> None:
        super().__init__()
        self._pool = pool
        self._storage_root = storage_root
        self._storage_prefix = storage_prefix
        self._vehicle_id = vehicle_id
        self._sensor_id = sensor_id
        self._start_time = start_time
        self._end_time = end_time
        self._ready_threshold_seconds = ready_threshold_seconds
        self._file_refind_count = file_refind_count
        self._file_refind_sleep_time = file_refind_sleep_time
        self._on_ready = on_ready
        self._on_error = on_error
        self._first_packet_time: float = 0.0

    def action(self) -> None:
        try:
            self._read_loop()
        except Exception as exc:
            if self._on_error is not None:
                self._on_error(exc)
            raise

    def _read_loop(self) -> None:
        category = SensorCategory.get(self._sensor_id)
        if category is None:
            raise ValueError(f"unknown sensor: {self._sensor_id}")

        start_dt = datetime.strptime(self._start_time, _TIMESTAMP_FORMAT)
        end_dt = datetime.strptime(self._end_time, _TIMESTAMP_FORMAT)
        seconds_diff = int((end_dt - start_dt).total_seconds())

        ready_ratio = min(seconds_diff, self._ready_threshold_seconds)
        ready_fired = False

        multi_reader = MultiPcapReader()
        cursor = start_dt

        for second_index in range(seconds_diff):
            if self.is_stop():
                return

            file_path = self._build_pcap_path(category, cursor)
            if not self._find_file_with_retry(file_path):
                raise FileNotFoundError(file_path)

            reader = multi_reader.read(file_path)

            for packet in reader.pool.packets:
                if self.is_stop():
                    return
                self._wait_until_appendable(packet)

            if second_index == 0 and reader.pool.size > 0:
                self._first_packet_time = reader.pool.packets[0].time.time_stamp

            cursor += timedelta(seconds=1)

            if not ready_fired and (second_index + 1) >= ready_ratio:
                ready_fired = True
                if self._on_ready is not None:
                    self._on_ready(self._first_packet_time)

        # ready_ratio 도달 전 read가 끝났으면 EOF 시점에도 ready 발화
        if not ready_fired and self._on_ready is not None:
            self._on_ready(self._first_packet_time)

    def _wait_until_appendable(self, packet) -> None:
        while not self._pool.append(packet):
            if self.is_stop():
                return
            time.sleep(0.01)

    def _find_file_with_retry(self, file_path: str) -> bool:
        for _ in range(self._file_refind_count):
            if os.path.isfile(file_path):
                return True
            time.sleep(self._file_refind_sleep_time)
            if self.is_stop():
                return False
        return os.path.isfile(file_path)

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

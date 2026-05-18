from __future__ import annotations

from datetime import datetime, timedelta

from python_library.storage.storage import IStorage
from python_library.thread.thread import abThread


MINUTE_FORMAT = "%Y%m%d%H%M"
TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"


class DownloadThread(abThread):
    """source storage → cache storage 파일 전송 thread.

    LookupThread와 같은 분 단위 path 순회 패턴이지만, 매 파일을 read 후
    cache로 write까지 수행. 운영에서는 source가 원격(S3/MinIO)으로 교체되고
    cache는 항상 LocalStorage.
    """

    def __init__(
        self,
        source_storage: IStorage,
        cache_storage: IStorage,
        source_root: str,
        source_prefix: str,
        cache_root: str,
        cache_prefix: str,
        vehicle_id: str,
        sensor_id: str,
        category: str,
        start_time: str,
        end_time: str,
    ) -> None:
        super().__init__()
        self._source_storage = source_storage
        self._cache_storage = cache_storage
        self._source_root = source_root
        self._source_prefix = source_prefix
        self._cache_root = cache_root
        self._cache_prefix = cache_prefix
        self._vehicle_id = vehicle_id
        self._sensor_id = sensor_id
        self._category = category
        self._start_time = start_time
        self._end_time = end_time

        self._error: Exception | None = None
        self._downloaded_count: int = 0

    def action(self) -> None:
        try:
            self.__transfer_loop()
        except Exception as e:
            self._error = e

    def get_error(self) -> Exception | None:
        return self._error

    def get_downloaded_count(self) -> int:
        return self._downloaded_count

    def __transfer_loop(self) -> None:
        cursor = datetime.strptime(self._start_time[:12], MINUTE_FORMAT)
        end_minute = datetime.strptime(self._end_time[:12], MINUTE_FORMAT)

        while cursor <= end_minute:
            if self.is_stop():
                return

            src_minute_path = self.__build_minute_path(
                self._source_root, self._source_prefix, cursor
            )
            cache_minute_path = self.__build_minute_path(
                self._cache_root, self._cache_prefix, cursor
            )

            for storage_file in self.__list_minute(src_minute_path):
                if self.is_stop():
                    return
                if storage_file.is_dir():
                    continue

                file_name = storage_file.get_file_name()
                ts = file_name.split(".")[0][-14:]
                if len(ts) != 14 or not ts.isdigit():
                    continue
                if not (self._start_time <= ts <= self._end_time):
                    continue

                src_path = f"{src_minute_path}{file_name}"
                cache_path = f"{cache_minute_path}{self._sensor_id}_{ts}.pcap"

                data = self._source_storage.read(src_path)
                self._cache_storage.write(cache_path, data)
                self._downloaded_count += 1

            cursor += timedelta(minutes=1)

    def __build_base_path(self, root: str, prefix: str) -> str:
        parts = [prefix, self._vehicle_id, self._category, self._sensor_id]
        suffix = "/".join(p for p in parts if p)
        return f"{root}/{suffix}"

    def __build_minute_path(self, root: str, prefix: str, when: datetime) -> str:
        base = self.__build_base_path(root, prefix)
        return f"{base}/{when.strftime('%Y%m%d')}/{when.strftime('%H')}/{when.strftime('%M')}/"

    def __list_minute(self, minute_path: str) -> list:
        # S3StorageClient (python-library v2.11.1) 가 빈 prefix 에서 KeyError('Contents').
        try:
            return self._source_storage.get_file_list(minute_path)
        except KeyError:
            return []

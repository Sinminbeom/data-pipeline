from __future__ import annotations

from typing import Callable, Optional

from pcaps.pool import PcapPool

from app.streamer.process.module.state.helper.pcap_reader_thread import PcapReaderThread
from app.streamer.process.module.state.helper.pcap_sender_thread import PcapSenderThread

ReadyCallback = Callable[[float], None]
CompleteCallback = Callable[[], None]
ErrorCallback = Callable[[Exception], None]


class PcapPlayer:
    """Reader + Sender 2 thread + Pool buffer orchestrator.

    구조:
        PcapReaderThread (producer) → PcapPool (buffer) → PcapSenderThread (consumer)

    라이프사이클:
        start() — 두 thread 시작
        pause() / resume() — sender 송출 일시정지/재개 (reader는 영향 없음)
        seek(start, end) — reader 교체 + pool clear + 재시작 (sender는 그대로)
        stop() / close() — reader/sender 모두 join (둘 다 동일 동작)
    """

    def __init__(
        self,
        storage_root: str,
        storage_prefix: str,
        vehicle_id: str,
        sensor_id: str,
        start_time: str,
        end_time: str,
        target_ip: str,
        target_port: int,
        buffer_size: int,
        ready_threshold_seconds: int = 2,
        file_refind_count: int = 3,
        file_refind_sleep_time: float = 0.1,
        on_ready: Optional[ReadyCallback] = None,
        on_complete: Optional[CompleteCallback] = None,
        on_error: Optional[ErrorCallback] = None,
    ) -> None:
        self._storage_root = storage_root
        self._storage_prefix = storage_prefix
        self._vehicle_id = vehicle_id
        self._sensor_id = sensor_id
        self._ready_threshold_seconds = ready_threshold_seconds
        self._file_refind_count = file_refind_count
        self._file_refind_sleep_time = file_refind_sleep_time
        self._on_ready = on_ready
        self._on_complete = on_complete
        self._on_error = on_error
        self._end_time = end_time   # seek 시 새 start_time과 결합

        self._pool: PcapPool = PcapPool(max_size=buffer_size)
        self._reader: PcapReaderThread = self._make_reader(start_time, end_time)
        self._sender: PcapSenderThread = PcapSenderThread(
            pool=self._pool,
            target_ip=target_ip,
            target_port=target_port,
            on_complete=on_complete,
            on_error=on_error,
        )

    def _make_reader(self, start_time: str, end_time: str) -> PcapReaderThread:
        return PcapReaderThread(
            pool=self._pool,
            storage_root=self._storage_root,
            storage_prefix=self._storage_prefix,
            vehicle_id=self._vehicle_id,
            sensor_id=self._sensor_id,
            start_time=start_time,
            end_time=end_time,
            ready_threshold_seconds=self._ready_threshold_seconds,
            file_refind_count=self._file_refind_count,
            file_refind_sleep_time=self._file_refind_sleep_time,
            on_ready=self._on_ready,
            on_error=self._on_error,
        )

    def start(self) -> None:
        self._reader.start()
        self._sender.start()

    def pause(self) -> None:
        """송출 일시정지. reader는 계속 buffer 채움."""
        self._sender.pause()

    def resume(self) -> None:
        self._sender.resume()

    def seek(self, start_time: str) -> None:
        """reader cursor 재설정 — 기존 reader stop + pool clear + 새 reader start.

        end_time은 init 시점 값 유지. sender는 pause 중이면 resume 포함.
        """
        self._reader.stop()
        self._reader.join()
        self._pool.clear()
        self._reader = self._make_reader(start_time, self._end_time)
        self._reader.start()
        self._sender.resume()

    def stop(self) -> None:
        """reader/sender 모두 종료 + join."""
        self._reader.stop()
        self._sender.stop()
        self._reader.join()
        self._sender.join()

    def close(self) -> None:
        """stop과 동일 동작."""
        self.stop()

    def join(self) -> None:
        self._reader.join()
        self._sender.join()

    @property
    def pool(self) -> PcapPool:
        return self._pool

    @property
    def is_paused(self) -> bool:
        return self._sender.is_pause()

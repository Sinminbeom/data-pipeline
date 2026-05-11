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

    외부 API:
        start() — 두 thread 시작
        stop()  — 두 thread 종료
        on_ready / on_complete / on_error callback으로 외부 통보
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
        self._pool: PcapPool = PcapPool(max_size=buffer_size)

        self._reader = PcapReaderThread(
            pool=self._pool,
            storage_root=storage_root,
            storage_prefix=storage_prefix,
            vehicle_id=vehicle_id,
            sensor_id=sensor_id,
            start_time=start_time,
            end_time=end_time,
            ready_threshold_seconds=ready_threshold_seconds,
            file_refind_count=file_refind_count,
            file_refind_sleep_time=file_refind_sleep_time,
            on_ready=on_ready,
            on_error=on_error,
        )

        self._sender = PcapSenderThread(
            pool=self._pool,
            target_ip=target_ip,
            target_port=target_port,
            on_complete=on_complete,
            on_error=on_error,
        )

    def start(self) -> None:
        self._reader.start()
        self._sender.start()

    def stop(self) -> None:
        self._reader.stop()
        self._sender.stop()

    def join(self) -> None:
        self._reader.join()
        self._sender.join()

    @property
    def pool(self) -> PcapPool:
        return self._pool

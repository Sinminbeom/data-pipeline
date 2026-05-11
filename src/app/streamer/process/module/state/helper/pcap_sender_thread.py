from __future__ import annotations

import socket
import time
from typing import Callable, Optional

from python_library.thread.thread import abThread

from pcaps.pool import PcapPool

CompleteCallback = Callable[[], None]
ErrorCallback = Callable[[Exception], None]


class PcapSenderThread(abThread):
    """PcapPool에서 패킷 꺼내 time.offset_time 만큼 sleep 후 UDP 송출 consumer thread.

    replayer App/Streamer/GStreamer/State/Helper/PcapSenderThread.py 미러.
    """

    def __init__(
        self,
        pool: PcapPool,
        target_ip: str,
        target_port: int,
        on_complete: Optional[CompleteCallback] = None,
        on_error: Optional[ErrorCallback] = None,
    ) -> None:
        super().__init__()
        self._pool = pool
        self._target_ip = target_ip
        self._target_port = target_port
        self._on_complete = on_complete
        self._on_error = on_error
        self._socket: Optional[socket.socket] = None

    def action(self) -> None:
        try:
            self._send_loop()
        except Exception as exc:
            if self._on_error is not None:
                self._on_error(exc)
            raise
        finally:
            self._close_socket()

    def _send_loop(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        consecutive_empty = 0
        max_empty_before_complete = 100  # 1초 (10ms * 100) empty면 EOF로 간주

        while not self.is_stop():
            packet = self._pool.pop_front()
            if packet is None:
                consecutive_empty += 1
                if consecutive_empty >= max_empty_before_complete:
                    break
                time.sleep(0.01)
                continue

            consecutive_empty = 0

            offset = packet.time.offset_time
            if offset > 0:
                time.sleep(offset)

            payload = packet.body.payload
            if payload:
                self._socket.sendto(payload, (self._target_ip, self._target_port))

        if self._on_complete is not None:
            self._on_complete()

    def _close_socket(self) -> None:
        if self._socket is not None:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None

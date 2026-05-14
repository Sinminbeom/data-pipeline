from __future__ import annotations

import time

from python_library.logger.app_logger import AppLogger

from common.event_bus.listener.listener import abListener
from common.process.queue_control_process import QueueControlProcess
from protocol.protocol_meta import ProtocolMeta
from protocol.protocol_wrapper import ProtocolWrapper


class InnerQueueListener(abListener[QueueControlProcess]):
    def __init__(self, parent_process: QueueControlProcess) -> None:
        super().__init__(parent_process)

    def action(self) -> None:
        envelope = self._parent_process.pop_shared_queue(self._parent_process.name)
        if envelope is None:
            time.sleep(0.001)
            return

        splits = ProtocolWrapper.get_split_protocol_message(envelope)
        receiver = ProtocolWrapper.get_receiver_with_splits(splits)

        wrapper, packet = ProtocolWrapper.decode_protocol_wrapper_with_message_protocol(envelope)

        log = AppLogger.instance()
        log.info(f"[INNER_QUEUE RECV] {wrapper.summary(packet)}")
        log.debug(f"[INNER_QUEUE RECV payload] {envelope}")

        # 1. 개별 핸들러 (응답마다 1회)
        ProtocolMeta.get_receive_handler(wrapper.protocol_id, receiver)(
            self._parent_process, wrapper, packet
        )

        # 2. 그룹 매처 누적 — matcher 미활성화면 내부에서 no-op
        self._parent_process.inr_matcher_on_response(wrapper, packet)

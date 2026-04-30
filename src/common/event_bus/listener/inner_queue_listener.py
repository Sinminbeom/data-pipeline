from __future__ import annotations

import time

from common.event_bus.listener.listener import abListener
from common.process.app_process import AppProcess
from protocol.protocol_meta import ProtocolMeta
from protocol.protocol_wrapper import ProtocolWrapper


class InnerQueueListener(abListener[AppProcess]):
    def __init__(self, parent_process: AppProcess) -> None:
        super().__init__(parent_process)

    def action(self) -> None:
        envelope = self._parent_process.pop_shared_queue(self._parent_process.name)
        if envelope is None:
            time.sleep(0.001)
            return

        splits = ProtocolWrapper.get_split_protocol_message(envelope)
        receiver = ProtocolWrapper.get_receiver_with_splits(splits)

        wrapper, packet = ProtocolWrapper.decode_protocol_wrapper_with_message_protocol(envelope)
        ProtocolMeta.get_receive_handler(wrapper.protocol_id, receiver)(
            self._parent_process, wrapper, packet
        )

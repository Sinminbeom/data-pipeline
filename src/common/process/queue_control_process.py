from __future__ import annotations

from typing import Optional

from common.process.step_process import StepProcess
from protocol.inr_protocol_matcher.inr_pair_state import E_PROTOCOL_PAIR_STATE
from protocol.inr_protocol_matcher.inr_protocol_matcher import InrProtocolMatcher
from protocol.message.message import IMessage, ResponseInfo
from protocol.protocol_meta import ProtocolMeta
from protocol.protocol_wrapper import ProtocolWrapper


class QueueControlProcess(StepProcess):
    def __init__(self, app_name: str, process_name: str) -> None:
        super().__init__(app_name, process_name)

        self._inner_queue_bus = None
        self._inr_matcher: Optional[InrProtocolMatcher] = None

    def on_init(self):
        # lazy import — InnerQueueBus가 QueueControlProcess를 직접 참조하므로 circular 방지
        from common.event_bus.inner_queue_bus import InnerQueueBus
        self._inner_queue_bus = InnerQueueBus(self)
        self._inner_queue_bus.start()
        pass

    def send_message_inner_queue(self, receiver_process_name: str, message: str) -> None:
        assert self._inner_queue_bus is not None
        self._inner_queue_bus.send_message_inner_queue(receiver_process_name, message)

    def send_message_req_inner_queue(
        self,
        protocol_id,
        receiver_process_name: str,
        *args,
    ) -> None:
        assert self._inner_queue_bus is not None
        self._inner_queue_bus.send_message_req_inner_queue(protocol_id, receiver_process_name, *args)

    def broadcast_message_req_inner_queue(
        self,
        protocol_id,
        receiver_process_names: list[str],
        *args,
        rep_protocol_id=None,
    ) -> None:
        """N개 receiver에 동일 REQ를 fan-out 송신.

        rep_protocol_id가 주어지면 매처에 group_id + expected_size를 자동 등록.
        매처가 활성화되지 않은 process면 등록은 no-op.
        """
        assert self._inner_queue_bus is not None

        if rep_protocol_id is not None:
            group_id = rep_protocol_id.value if hasattr(rep_protocol_id, "value") else rep_protocol_id
            self.inr_matcher_register_broadcast(group_id, len(receiver_process_names))

        self._inner_queue_bus.broadcast_message_req_inner_queue(
            protocol_id, receiver_process_names, *args
        )

    def send_message_rep_inner_queue(
        self,
        protocol_id,
        receiver_process_name: str,
        *args,
        response: ResponseInfo,
    ) -> None:
        assert self._inner_queue_bus is not None
        self._inner_queue_bus.send_message_rep_inner_queue(
            protocol_id, receiver_process_name, *args, response=response
        )

    # ---------------------------
    # INR group matcher (replayer 패턴 미러)
    # ---------------------------
    def enable_inr_matcher(self) -> QueueControlProcess:
        """builder. broadcast scatter-gather 그룹 콜백을 받을 process가 호출."""
        self._inr_matcher = InrProtocolMatcher()
        return self

    def inr_matcher_register_broadcast(self, group_id: str, expected_size: int) -> None:
        """broadcast 송신 직전 호출. group_id로 expected_size 등록."""
        if self._inr_matcher is None:
            return
        self._inr_matcher.register_broadcast(group_id, expected_size)

    def inr_matcher_on_response(self, wrapper: ProtocolWrapper, packet: IMessage) -> None:
        """listener가 응답 수신 시 자동 호출. 누적 → COMPLEATE/ERROR 도달 시 그룹 콜백 발화."""
        if self._inr_matcher is None:
            return

        from protocol.message.message import E_PROTOCOL_MESSAGE_DIRECTION
        if packet.message_direction != E_PROTOCOL_MESSAGE_DIRECTION.RESPONSE:
            return

        group_id = wrapper.protocol_id
        if not self._inr_matcher.has_group(group_id):
            return

        state = self._inr_matcher.append_response(group_id, packet)
        if state in (E_PROTOCOL_PAIR_STATE.COMPLEATE, E_PROTOCOL_PAIR_STATE.ERROR):
            handler = ProtocolMeta.get_inr_group_receive_handler(
                wrapper.protocol_id, self.get_app_name()
            )
            if handler is not None:
                handler(self, state, self._inr_matcher.get_responses(group_id))
            self._inr_matcher.clear(group_id)

    def on_proc_once(self):
        pass

    def on_proc_every_frame(self):
        pass

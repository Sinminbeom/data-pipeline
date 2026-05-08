from __future__ import annotations

from pcaps.packet import PcapPacket


class PcapPool:
    """PcapPacket 누적 보관 + active flag 관리.

    Wrapper 클래스 없이 dict[index → bool]로 단순화.
    """

    def __init__(self) -> None:
        self._packets: list[PcapPacket] = []
        self._active: dict[int, bool] = {}

    def append(self, packet: PcapPacket) -> None:
        index = len(self._packets)
        self._packets.append(packet)
        self._active[index] = True

    def get(self, index: int) -> PcapPacket:
        return self._packets[index]

    def is_active(self, index: int) -> bool:
        return self._active.get(index, False)

    def set_active(self, index: int, active: bool) -> None:
        self._active[index] = active

    @property
    def size(self) -> int:
        return len(self._packets)

    @property
    def packets(self) -> list[PcapPacket]:
        return self._packets

    def _first_active_index(self) -> int:
        """이진 탐색 — active=False가 앞에서부터 채워질 때 첫 active=True 인덱스."""
        left, right = 0, self.size - 1
        while left <= right:
            mid = (left + right) // 2
            if self.is_active(mid) and (mid == 0 or self.is_active(mid - 1) is False):
                return mid
            if self.is_active(mid):
                right = mid - 1
            else:
                left = mid + 1
        return -1

    def pop_with_time_stamp(self, accumulate_offset_time: float) -> None:
        # 원본 동작 보존 — 현재 placeholder
        index = self._first_active_index()
        print(f"ind:{index}")

    def println(self) -> None:
        for packet in self._packets:
            print(
                f" N : {packet.no:>5} "
                f" ts : {packet.header.time_str}  "
                f" t:{packet.time.time_stamp:<20} "
                f" of : {packet.time.offset_time:<22} "
                f" auof : {packet.time.accumulate_offset_time} "
                f" w_auof : {packet.time.world_accumulate_offset_time} "
                f" dpayload_size:{len(packet.payload)}"
            )

"""Pause semantic deep validation — UDP 송출 rate가 0으로 떨어지는지 검증."""
from tests.test_client._udp_helper import validate_lifecycle_stops_udp


def test_pause_stops_udp(fake_pcaps):
    """Play 중 UDP packet 도착 → PD_PAUSE → packet 멈춤 검증.

    PcapSenderThread.pause()가 송출 thread의 pause_event를 set해 송출 loop가
    sleep만 하는 상태가 되는 본체 동작을 e2e로 확인.
    """
    validate_lifecycle_stops_udp(
        fake_pcaps,
        lifecycle_req_id="PD_400",
        lifecycle_rep_id="PD_401",
    )

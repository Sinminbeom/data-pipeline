"""Stop semantic deep validation — UDP 송출 rate가 0으로 떨어지는지 검증."""
from tests.test_client._udp_helper import validate_lifecycle_stops_udp


def test_stop_stops_udp(fake_pcaps):
    """Play 중 UDP packet 도착 → PD_STOP → packet 멈춤 검증.

    Stop은 player.stop()으로 reader/sender thread 모두 join. 송출이 영구
    중단됨을 e2e로 확인.
    """
    validate_lifecycle_stops_udp(
        fake_pcaps,
        lifecycle_req_id="PD_600",
        lifecycle_rep_id="PD_601",
    )

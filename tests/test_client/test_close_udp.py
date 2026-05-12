"""Close semantic deep validation — UDP 송출 rate가 0으로 떨어지는지 검증."""
from tests.test_client._udp_helper import validate_lifecycle_stops_udp


def test_close_stops_udp(fake_pcaps):
    """Play 중 UDP packet 도착 → PD_CLOSE → packet 멈춤 검증.

    Close는 player.close() (= stop과 동일 동작, replayer 미러). reader/sender
    모두 join되어 송출 중단됨을 e2e로 확인.
    """
    validate_lifecycle_stops_udp(
        fake_pcaps,
        lifecycle_req_id="PD_300",
        lifecycle_rep_id="PD_301",
    )

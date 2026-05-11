from tests.test_client._lifecycle_helper import run_lifecycle_scenario


def test_play_then_pause(fake_pcaps):
    """PlayableList → Play → Pause 시나리오.

    full flow:
        client → REST_SERVER → STREAMER Manager (PAUSE) → STREAMER Module
              ← REST_SERVER ← MESSAGE_BRIDGE ← STREAMER Manager (PD_PAUSE_REP)
    """
    result = run_lifecycle_scenario(
        vehicle_id=fake_pcaps.vehicle_id,
        sensor_id_list=fake_pcaps.sensor_id_list,
        start_time=fake_pcaps.start_time,
        end_time=fake_pcaps.end_time,
        lifecycle_req_id="PD_400",
        lifecycle_rep_id="PD_401",
    )

    assert result.lifecycle_rep["protocol_id"] == "PD_401"
    print(f"[client] pause code={result.lifecycle_rep.get('code')} reason={result.lifecycle_rep.get('reason')}")

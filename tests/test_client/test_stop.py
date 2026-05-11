from tests.test_client._lifecycle_helper import run_lifecycle_scenario


def test_play_then_stop(fake_pcaps):
    """PlayableList → Play → Stop 시나리오.

    Stop은 reader/sender thread를 모두 join.
    """
    result = run_lifecycle_scenario(
        vehicle_id=fake_pcaps.vehicle_id,
        sensor_id_list=fake_pcaps.sensor_id_list,
        start_time=fake_pcaps.start_time,
        end_time=fake_pcaps.end_time,
        lifecycle_req_id="PD_600",
        lifecycle_rep_id="PD_601",
    )

    assert result.lifecycle_rep["protocol_id"] == "PD_601"
    print(f"[client] stop code={result.lifecycle_rep.get('code')} reason={result.lifecycle_rep.get('reason')}")

from tests.test_client._lifecycle_helper import run_lifecycle_scenario


def test_play_then_close(fake_pcaps):
    """PlayableList → Play → Close 시나리오.

    Close는 reader/sender thread를 모두 join — Stop과 동일 동작 (replayer 미러).
    """
    result = run_lifecycle_scenario(
        vehicle_id=fake_pcaps.vehicle_id,
        sensor_id_list=fake_pcaps.sensor_id_list,
        start_time=fake_pcaps.start_time,
        end_time=fake_pcaps.end_time,
        lifecycle_req_id="PD_300",
        lifecycle_rep_id="PD_301",
    )

    assert result.lifecycle_rep["protocol_id"] == "PD_301"
    print(f"[client] close code={result.lifecycle_rep.get('code')} reason={result.lifecycle_rep.get('reason')}")

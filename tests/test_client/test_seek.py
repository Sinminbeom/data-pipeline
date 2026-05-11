from tests.test_client._lifecycle_helper import run_lifecycle_scenario


def test_play_then_seek(fake_pcaps):
    """PlayableList → Play → Seek 시나리오.

    Seek는 PCAP reader cursor 재설정 — section 범위 안의 다른 시각으로 이동.
    """
    seek_target = {"value": None}

    def remember_seek(section: dict) -> None:
        seek_target["value"] = section["startTime"]

    result = run_lifecycle_scenario(
        vehicle_id=fake_pcaps.vehicle_id,
        sensor_id_list=fake_pcaps.sensor_id_list,
        start_time=fake_pcaps.start_time,
        end_time=fake_pcaps.end_time,
        lifecycle_req_id="PD_500",
        lifecycle_rep_id="PD_501",
        extra_payload={"start_time": fake_pcaps.start_time},
        on_section=remember_seek,
    )

    assert result.lifecycle_rep["protocol_id"] == "PD_501"
    print(f"[client] seek code={result.lifecycle_rep.get('code')} reason={result.lifecycle_rep.get('reason')}")

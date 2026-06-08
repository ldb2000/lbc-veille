import mqtt_client


def test_discovery_topic_format():
    assert (
        mqtt_client.discovery_topic("lbc_total_active")
        == "homeassistant/sensor/lbc_total_active/config"
    )


def test_build_discovery_total_active():
    sensor = next(s for s in mqtt_client.SENSORS if s["object_id"] == "lbc_total_active")
    cfg = mqtt_client.build_discovery(sensor)
    assert cfg["unique_id"] == "lbc_total_active"
    assert cfg["state_topic"] == "lbc_veille/state"
    assert cfg["availability_topic"] == "lbc_veille/availability"
    assert cfg["value_template"] == "{{ value_json.total_active }}"
    assert cfg["state_class"] == "measurement"
    assert cfg["device"]["identifiers"] == ["lbc_veille"]


def test_build_discovery_last_run_has_timestamp_and_attributes():
    sensor = next(s for s in mqtt_client.SENSORS if s["object_id"] == "lbc_last_run")
    cfg = mqtt_client.build_discovery(sensor)
    assert cfg["device_class"] == "timestamp"
    assert cfg["value_template"] == "{{ value_json.last_run }}"
    assert cfg["json_attributes_topic"] == "lbc_veille/state"


def test_four_sensors_declared():
    ids = {s["object_id"] for s in mqtt_client.SENSORS}
    assert ids == {
        "lbc_total_active",
        "lbc_new_last_run",
        "lbc_price_drops",
        "lbc_last_run",
    }

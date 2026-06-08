"""Publication MQTT discovery + état pour Home Assistant."""
import json

import paho.mqtt.client as mqtt

DISCOVERY_PREFIX = "homeassistant"
NODE = "lbc_veille"
STATE_TOPIC = f"{NODE}/state"
AVAIL_TOPIC = f"{NODE}/availability"

DEVICE = {
    "identifiers": [NODE],
    "name": "LBC Veille Motos",
    "manufacturer": "ldb2000",
    "model": "lbc-veille",
}

# attributes_all=True -> tout le JSON d'état devient attributs du capteur.
SENSORS = [
    {
        "object_id": "lbc_total_active",
        "name": "Annonces actives",
        "field": "total_active",
        "icon": "mdi:motorbike",
        "state_class": "measurement",
    },
    {
        "object_id": "lbc_new_last_run",
        "name": "Nouvelles (dernier run)",
        "field": "new_last_run",
        "icon": "mdi:new-box",
        "state_class": "measurement",
    },
    {
        "object_id": "lbc_price_drops",
        "name": "Baisses de prix (dernier run)",
        "field": "price_drops",
        "icon": "mdi:trending-down",
        "state_class": "measurement",
    },
    {
        "object_id": "lbc_last_run",
        "name": "Dernier scrape",
        "field": "last_run",
        "device_class": "timestamp",
        "attributes_all": True,
    },
]


def discovery_topic(object_id):
    """Topic de config discovery d'un capteur."""
    return f"{DISCOVERY_PREFIX}/sensor/{object_id}/config"


def build_discovery(sensor):
    """Construit le payload de config discovery d'un capteur. Fonction pure."""
    cfg = {
        "name": sensor["name"],
        "unique_id": sensor["object_id"],
        "object_id": sensor["object_id"],
        "state_topic": STATE_TOPIC,
        "availability_topic": AVAIL_TOPIC,
        "value_template": "{{ value_json.%s }}" % sensor["field"],
        "device": DEVICE,
    }
    for key in ("icon", "state_class", "device_class"):
        if key in sensor:
            cfg[key] = sensor[key]
    if sensor.get("attributes_all"):
        cfg["json_attributes_topic"] = STATE_TOPIC
    return cfg


class MqttPublisher:
    """Connexion MQTT + publication discovery/état/availability."""

    def __init__(self, host, port, username, password):
        self.client = mqtt.Client()
        if username:
            self.client.username_pw_set(username, password)
        self.client.will_set(AVAIL_TOPIC, "offline", retain=True)
        self.host = host
        self.port = int(port)

    def connect(self):
        self.client.connect(self.host, self.port, keepalive=60)
        self.client.loop_start()
        self.client.publish(AVAIL_TOPIC, "online", retain=True)

    def publish_discovery(self):
        for sensor in SENSORS:
            self.client.publish(
                discovery_topic(sensor["object_id"]),
                json.dumps(build_discovery(sensor)),
                retain=True,
            )

    def publish_state(self, payload):
        self.client.publish(STATE_TOPIC, json.dumps(payload), retain=True)

    def close(self):
        self.client.publish(AVAIL_TOPIC, "offline", retain=True)
        self.client.loop_stop()
        self.client.disconnect()

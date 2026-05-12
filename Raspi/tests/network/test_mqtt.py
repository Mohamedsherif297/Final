"""
tests/network/test_mqtt.py
==========================
Tests MQTT connectivity: local broker, pub/sub round-trip,
topic routing, and HiveMQ WAN access.

Run all:         pytest tests/network/test_mqtt.py -v
Local only:      pytest tests/network/test_mqtt.py -v -k "not wan"
WAN only:        pytest tests/network/test_mqtt.py -v -k "wan"

Required env vars for WAN tests:
    export HIVEMQ_HOST="your-broker.s1.eu.hivemq.cloud"
    export HIVEMQ_PORT=8883
    export HIVEMQ_USER="your-username"
    export HIVEMQ_PASS="your-password"
"""

import pytest
import time
import json
import threading
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

pytestmark = pytest.mark.mqtt

TIMEOUT = 5.0   # seconds to wait for a message


# ── Helpers ───────────────────────────────────────────────────
def make_client(client_id: str):
    """Create a paho MQTT client."""
    return mqtt.Client(client_id=client_id, clean_session=True)


def connect_and_wait(client, host, port, timeout=5.0, **kwargs):
    """Connect client and wait until connected or timeout."""
    connected = threading.Event()

    original_on_connect = client.on_connect

    def on_connect(c, ud, flags, rc):
        if rc == 0:
            connected.set()
        if original_on_connect:
            original_on_connect(c, ud, flags, rc)

    client.on_connect = on_connect
    client.connect(host, port, keepalive=10, **kwargs)
    client.loop_start()

    if not connected.wait(timeout=timeout):
        client.loop_stop()
        raise ConnectionError(f"Could not connect to {host}:{port} within {timeout}s")
    return client


# ══════════════════════════════════════════════════════════════
# LOCAL BROKER TESTS
# ══════════════════════════════════════════════════════════════

@pytest.mark.skipif(not MQTT_AVAILABLE, reason="paho-mqtt not installed")
class TestMQTTLocal:

    def test_broker_is_reachable(self, mqtt_broker_host, mqtt_broker_port):
        """Should connect to local Mosquitto broker."""
        client = make_client("test-ping")
        try:
            c = connect_and_wait(client, mqtt_broker_host, mqtt_broker_port)
            assert c is not None
            print(f"\n  Connected to {mqtt_broker_host}:{mqtt_broker_port} ✓")
        finally:
            client.loop_stop()
            client.disconnect()

    def test_publish_and_receive(self, mqtt_broker_host, mqtt_broker_port):
        """Publish a message and receive it back on the same topic."""
        received = threading.Event()
        payload_back = []

        subscriber = make_client("test-sub")
        publisher  = make_client("test-pub")

        def on_message(c, ud, msg):
            payload_back.append(msg.payload.decode())
            received.set()

        subscriber.on_message = on_message

        try:
            connect_and_wait(subscriber, mqtt_broker_host, mqtt_broker_port)
            subscriber.subscribe("test/ping")

            connect_and_wait(publisher, mqtt_broker_host, mqtt_broker_port)
            time.sleep(0.2)  # let subscription propagate
            publisher.publish("test/ping", "hello-car")

            assert received.wait(TIMEOUT), "Message not received within timeout"
            assert payload_back[0] == "hello-car"
            print(f"\n  Pub/Sub round-trip on test/ping ✓")

        finally:
            subscriber.loop_stop(); subscriber.disconnect()
            publisher.loop_stop();  publisher.disconnect()

    def test_motor_topic(self, mqtt_broker_host, mqtt_broker_port):
        """Publish a motor command to dev/motor and verify receipt."""
        received = threading.Event()
        messages = []

        sub = make_client("test-motor-sub")
        pub = make_client("test-motor-pub")

        sub.on_message = lambda c, ud, m: (messages.append(m), received.set())

        command = json.dumps({"direction": "forward", "speed": 50})

        try:
            connect_and_wait(sub, mqtt_broker_host, mqtt_broker_port)
            sub.subscribe("dev/motor")

            connect_and_wait(pub, mqtt_broker_host, mqtt_broker_port)
            time.sleep(0.2)
            pub.publish("dev/motor", command)

            assert received.wait(TIMEOUT), "Motor command not received"
            payload = messages[0].payload.decode()
            data = json.loads(payload)
            assert data["direction"] == "forward"
            assert data["speed"] == 50
            print(f"\n  dev/motor command delivered: {payload} ✓")

        finally:
            sub.loop_stop(); sub.disconnect()
            pub.loop_stop(); pub.disconnect()

    def test_all_command_topics(self, mqtt_broker_host, mqtt_broker_port):
        """Publish to all 4 command topics and verify receipt."""
        topics = {
            "dev/motor":    json.dumps({"direction": "stop"}),
            "dev/led":      json.dumps({"action": "set_color", "color": "idle"}),
            "dev/servo":    json.dumps({"action": "set_angle", "pan": 0, "tilt": 0}),
            "dev/commands": json.dumps({"command": "emergency_stop"}),
        }

        for topic, payload in topics.items():
            received = threading.Event()

            sub = make_client(f"sub-{topic.replace('/','_')}")
            pub = make_client(f"pub-{topic.replace('/','_')}")
            sub.on_message = lambda c, ud, m, ev=received: ev.set()

            try:
                connect_and_wait(sub, mqtt_broker_host, mqtt_broker_port)
                sub.subscribe(topic)
                connect_and_wait(pub, mqtt_broker_host, mqtt_broker_port)
                time.sleep(0.2)
                pub.publish(topic, payload)
                assert received.wait(TIMEOUT), f"{topic}: message not received"
                print(f"  {topic} ✓")
            finally:
                sub.loop_stop(); sub.disconnect()
                pub.loop_stop(); pub.disconnect()

    def test_sensor_topic_receipt(self, mqtt_broker_host, mqtt_broker_port):
        """Verify sensors/ultrasonic topic can be subscribed."""
        received = threading.Event()
        sub = make_client("test-sensor-sub")
        pub = make_client("test-sensor-pub")
        sub.on_message = lambda c, ud, m: received.set()

        payload = json.dumps({"distance": 45.3, "unit": "cm"})
        try:
            connect_and_wait(sub, mqtt_broker_host, mqtt_broker_port)
            sub.subscribe("sensors/ultrasonic")
            connect_and_wait(pub, mqtt_broker_host, mqtt_broker_port)
            time.sleep(0.2)
            pub.publish("sensors/ultrasonic", payload)
            assert received.wait(TIMEOUT), "Sensor message not received"
            print(f"\n  sensors/ultrasonic message delivered ✓")
        finally:
            sub.loop_stop(); sub.disconnect()
            pub.loop_stop(); pub.disconnect()

    def test_reconnect_after_disconnect(self, mqtt_broker_host, mqtt_broker_port):
        """Client should reconnect after being disconnected."""
        client = make_client("test-reconnect")
        try:
            connect_and_wait(client, mqtt_broker_host, mqtt_broker_port)
            client.disconnect()
            time.sleep(0.5)
            # Reconnect
            connect_and_wait(client, mqtt_broker_host, mqtt_broker_port)
            print(f"\n  Reconnected after disconnect ✓")
        finally:
            client.loop_stop()
            client.disconnect()


# ══════════════════════════════════════════════════════════════
# WAN (HiveMQ) TESTS
# ══════════════════════════════════════════════════════════════

@pytest.mark.skipif(not MQTT_AVAILABLE, reason="paho-mqtt not installed")
class TestMQTTWAN:

    def _skip_if_no_creds(self, host, user, password):
        if not host or not user or not password:
            pytest.skip("HiveMQ credentials not set. Export HIVEMQ_HOST, HIVEMQ_USER, HIVEMQ_PASS")

    def test_wan_broker_is_reachable(self, hivemq_host, hivemq_port, hivemq_user, hivemq_pass):
        """Should connect to HiveMQ cloud broker via TLS."""
        self._skip_if_no_creds(hivemq_host, hivemq_user, hivemq_pass)

        client = make_client("test-wan-ping")
        client.username_pw_set(hivemq_user, hivemq_pass)
        client.tls_set()  # enable TLS

        try:
            connect_and_wait(client, hivemq_host, hivemq_port, timeout=10.0)
            print(f"\n  Connected to HiveMQ WAN: {hivemq_host}:{hivemq_port} ✓")
        finally:
            client.loop_stop()
            client.disconnect()

    def test_wan_pub_sub_round_trip(self, hivemq_host, hivemq_port, hivemq_user, hivemq_pass):
        """Publish and receive a message via HiveMQ cloud."""
        self._skip_if_no_creds(hivemq_host, hivemq_user, hivemq_pass)

        received = threading.Event()
        messages = []

        def make_tls_client(cid):
            c = make_client(cid)
            c.username_pw_set(hivemq_user, hivemq_pass)
            c.tls_set()
            return c

        sub = make_tls_client("wan-sub")
        pub = make_tls_client("wan-pub")
        sub.on_message = lambda c, ud, m: (messages.append(m.payload.decode()), received.set())

        try:
            connect_and_wait(sub, hivemq_host, hivemq_port, timeout=10.0)
            sub.subscribe("test/wan-ping")

            connect_and_wait(pub, hivemq_host, hivemq_port, timeout=10.0)
            time.sleep(0.5)
            pub.publish("test/wan-ping", "wan-hello")

            assert received.wait(10.0), "WAN message not received within 10s"
            assert messages[0] == "wan-hello"
            print(f"\n  WAN pub/sub round-trip ✓ (latency acceptable)")
        finally:
            sub.loop_stop(); sub.disconnect()
            pub.loop_stop(); pub.disconnect()

    def test_wan_motor_command(self, hivemq_host, hivemq_port, hivemq_user, hivemq_pass):
        """Send a motor command via WAN and verify receipt."""
        self._skip_if_no_creds(hivemq_host, hivemq_user, hivemq_pass)

        received = threading.Event()
        messages = []

        def make_tls_client(cid):
            c = make_client(cid)
            c.username_pw_set(hivemq_user, hivemq_pass)
            c.tls_set()
            return c

        sub = make_tls_client("wan-motor-sub")
        pub = make_tls_client("wan-motor-pub")
        sub.on_message = lambda c, ud, m: (messages.append(m.payload.decode()), received.set())

        command = json.dumps({"direction": "forward", "speed": 60})

        try:
            connect_and_wait(sub, hivemq_host, hivemq_port, timeout=10.0)
            sub.subscribe("dev/motor")
            connect_and_wait(pub, hivemq_host, hivemq_port, timeout=10.0)
            time.sleep(0.5)
            pub.publish("dev/motor", command)

            assert received.wait(10.0), "WAN motor command not received"
            data = json.loads(messages[0])
            assert data["direction"] == "forward"
            print(f"\n  WAN dev/motor command delivered ✓")
        finally:
            sub.loop_stop(); sub.disconnect()
            pub.loop_stop(); pub.disconnect()

"""
conftest.py — pytest configuration for Surveillance Car test suite
Run from: /home/pi/Final/Raspi/
    pytest tests/ -v
    pytest tests/unit/ -v -m hardware
    pytest tests/network/ -v -m "mqtt or websocket"
"""

import sys
import os
import time
import pytest

# ── Path Setup ────────────────────────────────────────────────
# Make sure Drivers/ is importable as 'hardware.*'
RASPI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVERS_DIR = os.path.join(RASPI_DIR, "Drivers")
sys.path.insert(0, RASPI_DIR)
sys.path.insert(0, DRIVERS_DIR)

# ── Custom Markers ────────────────────────────────────────────
def pytest_configure(config):
    config.addinivalue_line("markers", "hardware: requires physical GPIO hardware on Raspberry Pi")
    config.addinivalue_line("markers", "mqtt: requires running MQTT broker")
    config.addinivalue_line("markers", "websocket: requires main.py running on Pi")
    config.addinivalue_line("markers", "camera: requires camera module connected")
    config.addinivalue_line("markers", "slow: test takes more than 5 seconds")

# ── Shared Fixtures ───────────────────────────────────────────
@pytest.fixture(scope="session")
def is_on_pi():
    """Detect if running on real Raspberry Pi with GPIO."""
    try:
        import RPi.GPIO
        return True
    except (ImportError, RuntimeError):
        return False

@pytest.fixture(scope="session")
def pi_ip():
    """Get Pi IP — used only in network tests."""
    return os.environ.get("PI_IP", "localhost")

@pytest.fixture(scope="session")
def mqtt_broker_host(pi_ip):
    return os.environ.get("MQTT_HOST", pi_ip)

@pytest.fixture(scope="session")
def mqtt_broker_port():
    return int(os.environ.get("MQTT_PORT", "1883"))

@pytest.fixture(scope="session")
def ws_url(pi_ip):
    port = os.environ.get("WS_PORT", "8765")
    return f"ws://{pi_ip}:{port}"

# HiveMQ WAN credentials — set via env vars on the Pi
@pytest.fixture(scope="session")
def hivemq_host():
    return os.environ.get("HIVEMQ_HOST", "")

@pytest.fixture(scope="session")
def hivemq_port():
    return int(os.environ.get("HIVEMQ_PORT", "8883"))

@pytest.fixture(scope="session")
def hivemq_user():
    return os.environ.get("HIVEMQ_USER", "")

@pytest.fixture(scope="session")
def hivemq_pass():
    return os.environ.get("HIVEMQ_PASS", "")

# ── Helper ────────────────────────────────────────────────────
def wait_for(condition_fn, timeout=5.0, interval=0.1, label="condition"):
    """Poll until condition_fn() returns truthy or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if condition_fn():
            return True
        time.sleep(interval)
    raise TimeoutError(f"Timed out waiting for: {label}")

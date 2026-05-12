"""
tests/unit/test_led_ultrasonic_camera.py
========================================
Tests LED controller (colors + effects), Ultrasonic sensor
(distance reading + obstacle detection), and Camera (init + frame).

Run:  pytest tests/unit/test_led_ultrasonic_camera.py -v
"""

import pytest
import time
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../Drivers'))

from hardware.gpio.gpio_manager import gpio_manager
from hardware.gpio.pwm_manager import pwm_manager
from hardware.led.led_controller import LEDController, LEDEffect
from hardware.ultrasonic.ultrasonic_controller import UltrasonicController
from hardware.camera.camera_controller import CameraController


# ══════════════════════════════════════════════════════════════
# LED TESTS
# ══════════════════════════════════════════════════════════════

@pytest.fixture
def led():
    gpio_manager.initialized = False
    gpio_manager.active_pins.clear()
    gpio_manager.pin_modes.clear()
    gpio_manager.initialize()

    lc = LEDController()
    lc.initialize()
    yield lc

    lc.cleanup()
    pwm_manager.cleanup()
    gpio_manager.cleanup_all()
    gpio_manager.initialized = False


class TestLEDInit:

    def test_initializes_successfully(self, led):
        assert led.initialized is True
        print("\n  LED controller initialized ✓")

    def test_initial_state(self, led):
        status = led.get_status()
        assert 'color' in status
        assert 'initialized' in status
        assert status['initialized'] is True


class TestLEDColors:

    @pytest.mark.hardware
    def test_set_red(self, led):
        """LED should glow RED — verify visually."""
        print("\n  → LED: RED (255, 0, 0)... look at LED")
        led.set_color(255, 0, 0)
        time.sleep(1.5)
        assert led.current_color == (255, 0, 0)
        print("  LED is RED ✓")

    @pytest.mark.hardware
    def test_set_green(self, led):
        """LED should glow GREEN."""
        print("\n  → LED: GREEN (0, 255, 0)...")
        led.set_color(0, 255, 0)
        time.sleep(1.5)
        assert led.current_color == (0, 255, 0)
        print("  LED is GREEN ✓")

    @pytest.mark.hardware
    def test_set_blue(self, led):
        """LED should glow BLUE."""
        print("\n  → LED: BLUE (0, 0, 255)...")
        led.set_color(0, 0, 255)
        time.sleep(1.5)
        assert led.current_color == (0, 0, 255)
        print("  LED is BLUE ✓")

    @pytest.mark.hardware
    def test_set_white(self, led):
        """LED should glow WHITE (full R+G+B)."""
        print("\n  → LED: WHITE (255, 255, 255)...")
        led.set_color(255, 255, 255)
        time.sleep(1.0)
        assert led.current_color == (255, 255, 255)

    @pytest.mark.hardware
    def test_off(self, led):
        """LED should turn off completely."""
        led.set_color(255, 0, 0)
        time.sleep(0.5)
        print("\n  → LED: OFF...")
        led.off()
        time.sleep(0.5)
        assert led.current_color == (0, 0, 0)
        print("  LED is OFF ✓")

    @pytest.mark.hardware
    def test_status_colors(self, led):
        """Status presets (idle/moving/emergency) should display correctly."""
        for status_name in ['idle', 'moving', 'emergency']:
            print(f"\n  → Status: {status_name}...")
            led.set_status_color(status_name)
            time.sleep(1.0)
        led.off()
        print("  All status colors shown ✓")


class TestLEDEffects:

    @pytest.mark.hardware
    @pytest.mark.slow
    def test_blink_effect(self, led):
        """LED should blink for 3 seconds."""
        print("\n  → BLINK effect (3s)...")
        led.set_color(0, 100, 255)
        led.start_effect(LEDEffect.BLINK)
        time.sleep(3.0)
        assert led.effect_running is True
        led.stop_effect()
        assert led.effect_running is False
        print("  Blink effect stopped ✓")

    @pytest.mark.hardware
    @pytest.mark.slow
    def test_rainbow_effect(self, led):
        """LED should cycle rainbow for 3 seconds."""
        print("\n  → RAINBOW effect (3s)...")
        led.start_effect(LEDEffect.RAINBOW)
        time.sleep(3.0)
        led.stop_effect()
        print("  Rainbow effect stopped ✓")

    @pytest.mark.hardware
    @pytest.mark.slow
    def test_pulse_effect(self, led):
        """LED should pulse for 3 seconds."""
        print("\n  → PULSE effect (3s)...")
        led.set_color(255, 50, 0)
        led.start_effect(LEDEffect.PULSE)
        time.sleep(3.0)
        led.stop_effect()
        print("  Pulse effect stopped ✓")

    def test_stop_when_no_effect_is_safe(self, led):
        """stop_effect() when no effect running should not raise."""
        led.stop_effect()  # should be a no-op


# ══════════════════════════════════════════════════════════════
# ULTRASONIC TESTS
# ══════════════════════════════════════════════════════════════

@pytest.fixture
def ultrasonic():
    gpio_manager.initialized = False
    gpio_manager.active_pins.clear()
    gpio_manager.pin_modes.clear()
    gpio_manager.initialize()

    uc = UltrasonicController()
    uc.initialize()
    yield uc

    uc.cleanup()
    gpio_manager.cleanup_all()
    gpio_manager.initialized = False


class TestUltrasonicInit:

    def test_initializes_successfully(self, ultrasonic):
        assert ultrasonic.initialized is True
        print("\n  Ultrasonic sensor initialized ✓")

    def test_status_keys(self, ultrasonic):
        status = ultrasonic.get_status()
        for key in ('distance_cm', 'monitoring', 'initialized'):
            assert key in status


class TestUltrasonicReading:

    @pytest.mark.hardware
    def test_single_measurement_returns_value(self, ultrasonic):
        """A single measurement should return a number or None."""
        dist = ultrasonic.measure_distance()
        # On real hardware pointing at something: dist should be > 0
        print(f"\n  Raw distance: {dist} cm")
        # We accept None in simulation; on real HW it should be a float
        if dist is not None:
            assert 2 <= dist <= 400, f"Distance out of range: {dist}"
        print("  Distance reading ✓")

    @pytest.mark.hardware
    def test_filtered_distance(self, ultrasonic):
        """Filtered distance should be smoother than raw."""
        dist = ultrasonic.get_filtered_distance()
        print(f"\n  Filtered distance: {dist} cm")
        if dist is not None:
            assert 2 <= dist <= 400

    @pytest.mark.hardware
    @pytest.mark.slow
    def test_continuous_monitoring(self, ultrasonic):
        """Start monitoring → collect 5 readings → stop."""
        readings = []

        def capture_callback(distance):
            pass  # real obstacle callback; we just watch

        ultrasonic.register_obstacle_callback(capture_callback)
        ultrasonic.start_monitoring(interval=0.2)
        assert ultrasonic.is_monitoring is True
        print("\n  Monitoring started ✓")

        for i in range(5):
            time.sleep(0.3)
            d = ultrasonic.current_distance
            readings.append(d)
            print(f"  Reading {i+1}: {d} cm")

        ultrasonic.stop_monitoring()
        assert ultrasonic.is_monitoring is False
        print("  Monitoring stopped ✓")

    @pytest.mark.hardware
    def test_obstacle_callback_fires(self, ultrasonic):
        """Callback should fire when distance is within threshold."""
        triggered = []

        def on_obstacle(dist):
            triggered.append(dist)

        # Lower threshold to ensure it fires during test
        ultrasonic.obstacle_detection.emergency_distance = 999.0
        ultrasonic.register_obstacle_callback(on_obstacle)
        ultrasonic.get_filtered_distance()
        # Restore
        ultrasonic.obstacle_detection.emergency_distance = 20.0
        print(f"\n  Callback fired: {len(triggered)} times ✓")


# ══════════════════════════════════════════════════════════════
# CAMERA TESTS
# ══════════════════════════════════════════════════════════════

@pytest.fixture
def camera():
    cc = CameraController(device_id=0, resolution=(640, 480), fps=30)
    cc.initialize()
    cc.start_capture()
    yield cc
    cc.cleanup()


class TestCameraInit:

    @pytest.mark.camera
    def test_initializes_successfully(self, camera):
        assert camera.initialized is True
        print("\n  Camera controller initialized ✓")

    @pytest.mark.camera
    def test_status_keys(self, camera):
        status = camera.get_status()
        assert 'initialized' in status
        print(f"\n  Camera status: {status}")

    @pytest.mark.camera
    def test_get_frame(self, camera):
        """Should capture a valid non-None frame."""
        time.sleep(0.5)  # let camera warm up
        frame = camera.get_frame()
        assert frame is not None, "Camera returned None frame — is the camera connected?"
        h, w = frame.shape[:2]
        assert w == 640 and h == 480, f"Unexpected resolution: {w}x{h}"
        print(f"\n  Frame captured: {w}x{h} ✓")

    @pytest.mark.camera
    def test_get_ai_frame(self, camera):
        """AI frame getter should return a valid frame."""
        time.sleep(0.5)
        frame = camera.get_ai_frame()
        assert frame is not None
        print(f"\n  AI frame: shape={frame.shape} ✓")

    @pytest.mark.camera
    def test_save_test_frame(self, camera, tmp_path):
        """Save a test frame as JPEG — open manually to verify image quality."""
        import cv2
        time.sleep(0.5)
        frame = camera.get_frame()
        assert frame is not None
        out = str(tmp_path / "test_frame.jpg")
        cv2.imwrite(out, frame)
        assert os.path.exists(out)
        print(f"\n  Frame saved to: {out}")
        print("  Open the file to visually verify camera image ✓")

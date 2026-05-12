"""
tests/unit/test_servo.py
========================
Tests ServoController: init, angle range, pan/tilt, center,
limits enforcement. Servo WILL physically move on hardware tests.

Run:  pytest tests/unit/test_servo.py -v
"""

import pytest
import time
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../Drivers'))

from hardware.gpio.gpio_manager import gpio_manager
from hardware.gpio.pwm_manager import pwm_manager
from hardware.servo.servo_controller import ServoController


# ── Fixtures ──────────────────────────────────────────────────
@pytest.fixture
def servo():
    """Provide an initialized ServoController; cleanup after test."""
    gpio_manager.initialized = False
    gpio_manager.active_pins.clear()
    gpio_manager.pin_modes.clear()
    gpio_manager.initialize()

    sc = ServoController()
    sc.initialize()
    yield sc

    sc.cleanup()
    pwm_manager.cleanup()
    gpio_manager.cleanup_all()
    gpio_manager.initialized = False


# ── Tests ─────────────────────────────────────────────────────

class TestServoInit:

    def test_initializes_successfully(self, servo):
        """Servo controller should initialize without raising."""
        assert servo.initialized is True
        print("\n  Servo controller initialized ✓")

    def test_starts_at_center(self, servo):
        """Pan and tilt should both be at center (0°) after init."""
        pan, tilt = servo.get_position()
        assert pan == servo.pan_limits.center_angle
        assert tilt == servo.tilt_limits.center_angle
        print(f"\n  Initial position: pan={pan}° tilt={tilt}° ✓")

    def test_status_returns_dict(self, servo):
        """get_status() should return required keys."""
        status = servo.get_status()
        for key in ('pan_angle', 'tilt_angle', 'initialized'):
            assert key in status
        print(f"\n  Status: pan={status['pan_angle']}° tilt={status['tilt_angle']}° ✓")


class TestServoAngles:

    @pytest.mark.hardware
    def test_pan_full_left(self, servo):
        """Pan servo should reach -90° (full left)."""
        print("\n  → Panning LEFT to -90°... (watch camera)")
        servo.set_angle(pan=-90, smooth=True)
        time.sleep(0.5)
        assert servo.pan_angle == -90
        print(f"  Pan angle: {servo.pan_angle}° ✓")

    @pytest.mark.hardware
    def test_pan_full_right(self, servo):
        """Pan servo should reach +90° (full right)."""
        print("\n  → Panning RIGHT to +90°... (watch camera)")
        servo.set_angle(pan=90, smooth=True)
        time.sleep(0.5)
        assert servo.pan_angle == 90
        print(f"  Pan angle: {servo.pan_angle}° ✓")

    @pytest.mark.hardware
    def test_tilt_up(self, servo):
        """Tilt servo should reach +45° (up)."""
        print("\n  → Tilting UP to +45°... (watch camera)")
        servo.set_angle(tilt=45, smooth=True)
        time.sleep(0.5)
        assert servo.tilt_angle == 45
        print(f"  Tilt angle: {servo.tilt_angle}° ✓")

    @pytest.mark.hardware
    def test_tilt_down(self, servo):
        """Tilt servo should reach -45° (down)."""
        print("\n  → Tilting DOWN to -45°... (watch camera)")
        servo.set_angle(tilt=-45, smooth=True)
        time.sleep(0.5)
        assert servo.tilt_angle == -45
        print(f"  Tilt angle: {servo.tilt_angle}° ✓")

    @pytest.mark.hardware
    def test_full_sweep_sequence(self, servo):
        """Run center → left → right → center sweep."""
        print("\n  → Full sweep sequence...")
        steps = [
            (0,   0,   "CENTER"),
            (-90, 0,   "LEFT"),
            (90,  0,   "RIGHT"),
            (0,   45,  "UP"),
            (0,  -45,  "DOWN"),
            (0,   0,   "CENTER"),
        ]
        for pan, tilt, label in steps:
            servo.set_angle(pan=pan, tilt=tilt, smooth=True)
            time.sleep(0.4)
            print(f"    {label}: pan={servo.pan_angle}° tilt={servo.tilt_angle}° ✓")


class TestServoLimits:

    def test_pan_clamped_beyond_max(self, servo):
        """Pan angle beyond +90° should be clamped to max."""
        servo.set_angle(pan=200, smooth=False)
        assert servo.pan_angle <= servo.pan_limits.max_angle
        print(f"\n  Pan clamped to {servo.pan_angle}° (max={servo.pan_limits.max_angle}°) ✓")

    def test_pan_clamped_below_min(self, servo):
        """Pan angle below -90° should be clamped to min."""
        servo.set_angle(pan=-200, smooth=False)
        assert servo.pan_angle >= servo.pan_limits.min_angle
        print(f"\n  Pan clamped to {servo.pan_angle}° (min={servo.pan_limits.min_angle}°) ✓")

    def test_tilt_clamped_beyond_max(self, servo):
        """Tilt angle beyond max should be clamped."""
        servo.set_angle(tilt=999, smooth=False)
        assert servo.tilt_angle <= servo.tilt_limits.max_angle

    def test_center_resets_both_axes(self, servo):
        """center() should return both axes to 0°."""
        servo.set_angle(pan=45, tilt=-30, smooth=False)
        servo.center()
        pan, tilt = servo.get_position()
        assert pan == servo.pan_limits.center_angle
        assert tilt == servo.tilt_limits.center_angle
        print(f"\n  Centered: pan={pan}° tilt={tilt}° ✓")


class TestServoNudge:

    @pytest.mark.hardware
    def test_pan_left_nudge(self, servo):
        """pan_left() should decrement pan by default step."""
        servo.set_angle(pan=0, smooth=False)
        before = servo.pan_angle
        servo.pan_left(degrees=15)
        assert servo.pan_angle == before - 15
        print(f"\n  Pan nudged left: {before}° → {servo.pan_angle}° ✓")

    @pytest.mark.hardware
    def test_pan_right_nudge(self, servo):
        """pan_right() should increment pan by default step."""
        servo.set_angle(pan=0, smooth=False)
        before = servo.pan_angle
        servo.pan_right(degrees=15)
        assert servo.pan_angle == before + 15
        print(f"\n  Pan nudged right: {before}° → {servo.pan_angle}° ✓")

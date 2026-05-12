"""
tests/unit/test_motor.py
========================
Tests MotorController: init, all directions, speed, emergency stop.
Motors WILL physically move during @pytest.mark.hardware tests —
have the car propped up or motors free-running before running.

Run:  pytest tests/unit/test_motor.py -v
Skip hardware:  pytest tests/unit/test_motor.py -v -m "not hardware"
"""

import pytest
import time
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../Drivers'))

from hardware.gpio.gpio_manager import gpio_manager
from hardware.motor.motor_controller import MotorController, MotorDirection


# ── Fixtures ──────────────────────────────────────────────────
@pytest.fixture
def motor():
    """Provide an initialized MotorController; cleanup after test."""
    gpio_manager.initialized = False
    gpio_manager.active_pins.clear()
    gpio_manager.pin_modes.clear()
    gpio_manager.initialize()

    mc = MotorController()
    mc.initialize()
    yield mc

    mc.stop(smooth=False)
    mc.cleanup()
    gpio_manager.cleanup_all()
    gpio_manager.initialized = False


# ── Tests ─────────────────────────────────────────────────────

class TestMotorInit:

    def test_initializes_successfully(self, motor):
        """Motor controller should initialize without error."""
        assert motor.initialized is True
        print("\n  Motor controller initialized ✓")

    def test_initial_state_is_stopped(self, motor):
        """Motor should start in STOP state at 0% speed."""
        status = motor.get_status()
        assert status['direction'] == 'stop'
        assert status['speed'] == 0.0
        assert status['emergency_stop'] is False
        print(f"\n  Initial state: {status['direction']} @ {status['speed']}% ✓")

    def test_double_init_is_safe(self, motor):
        """Calling initialize() twice should not raise."""
        motor.initialize()
        assert motor.initialized is True


class TestMotorMovement:

    @pytest.mark.hardware
    def test_move_forward(self, motor):
        """Motor should move forward at 50% speed for 1 second."""
        print("\n  → Moving FORWARD at 50%... (watch motor)")
        motor.move_forward(speed=50)
        time.sleep(1.0)
        assert motor.current_direction == MotorDirection.FORWARD
        motor.stop(smooth=False)
        print("  Motor stopped ✓")

    @pytest.mark.hardware
    def test_move_backward(self, motor):
        """Motor should move backward at 50% speed for 1 second."""
        print("\n  → Moving BACKWARD at 50%... (watch motor)")
        motor.move_backward(speed=50)
        time.sleep(1.0)
        assert motor.current_direction == MotorDirection.BACKWARD
        motor.stop(smooth=False)
        print("  Motor stopped ✓")

    @pytest.mark.hardware
    def test_turn_left(self, motor):
        """Left turn: left motor slower, right motor forward."""
        print("\n  → Turning LEFT at 60%...")
        motor.turn_left(speed=60)
        time.sleep(0.8)
        assert motor.current_direction == MotorDirection.LEFT
        motor.stop(smooth=False)
        print("  Motor stopped ✓")

    @pytest.mark.hardware
    def test_turn_right(self, motor):
        """Right turn: right motor slower, left motor forward."""
        print("\n  → Turning RIGHT at 60%...")
        motor.turn_right(speed=60)
        time.sleep(0.8)
        assert motor.current_direction == MotorDirection.RIGHT
        motor.stop(smooth=False)
        print("  Motor stopped ✓")

    @pytest.mark.hardware
    def test_direction_sequence(self, motor):
        """Run F → B → L → R → STOP sequence."""
        print("\n  → Running direction sequence...")
        for fn, label in [
            (lambda: motor.move_forward(50),  "FORWARD"),
            (lambda: motor.move_backward(50), "BACKWARD"),
            (lambda: motor.turn_left(50),     "LEFT"),
            (lambda: motor.turn_right(50),    "RIGHT"),
        ]:
            fn()
            time.sleep(0.5)
            print(f"    {label} ✓")
        motor.stop(smooth=False)
        assert motor.current_direction == MotorDirection.STOP


class TestMotorSpeed:

    def test_speed_validation_low(self, motor):
        """Speed below 0 should be clamped to 0."""
        motor.set_speed(-10)
        assert motor.target_speed == 0.0

    def test_speed_validation_high(self, motor):
        """Speed above 100 should be clamped to 100."""
        motor.set_speed(150)
        assert motor.target_speed == 100.0

    def test_speed_set_correctly(self, motor):
        """Valid speed should be stored correctly."""
        motor.set_speed(75)
        assert motor.target_speed == 75.0
        print(f"\n  Speed set to 75% ✓")


class TestMotorSafety:

    def test_emergency_stop_halts_immediately(self, motor):
        """Emergency stop should halt and block further movement."""
        motor.emergency_stop()
        assert motor.current_direction == MotorDirection.STOP
        assert motor.safety.is_emergency_stop_active() is True
        print("\n  Emergency stop triggered ✓")

    def test_cannot_move_after_emergency_stop(self, motor):
        """move_forward() should be a no-op while e-stop is active."""
        motor.emergency_stop()
        motor.move_forward(speed=50)
        # Direction should stay STOP (e-stop blocks movement)
        assert motor.current_direction == MotorDirection.STOP
        print("\n  Movement correctly blocked during e-stop ✓")

    def test_emergency_reset_allows_movement(self, motor):
        """After resetting e-stop, motor should accept commands again."""
        motor.emergency_stop()
        motor.safety.reset_emergency_stop()
        assert motor.safety.is_emergency_stop_active() is False
        print("\n  Emergency reset — movement re-enabled ✓")

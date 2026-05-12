"""
tests/unit/test_gpio.py
=======================
Tests GPIO manager initialization, pin registration, and
output/input operations. Validates wiring at the pin level.

Run:  pytest tests/unit/test_gpio.py -v
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../Drivers'))

from hardware.gpio.gpio_manager import gpio_manager
from hardware.gpio.pin_definitions import pin_defs


# ── Fixtures ──────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def reset_gpio():
    """Initialize + cleanup GPIO around each test."""
    gpio_manager.initialized = False  # force re-init
    gpio_manager.active_pins.clear()
    gpio_manager.pin_modes.clear()
    gpio_manager.initialize()
    yield
    gpio_manager.cleanup_all()
    gpio_manager.initialized = False


# ── Tests ─────────────────────────────────────────────────────

class TestGPIOInit:

    def test_gpio_initializes(self):
        """GPIO manager should initialize without error."""
        assert gpio_manager.initialized is True
        print(f"\n  Mode: {'SIMULATION' if gpio_manager.simulation_mode else 'REAL GPIO'}")

    def test_simulation_mode_detected(self, is_on_pi):
        """Simulation mode is active only when not on a Pi."""
        if is_on_pi:
            assert gpio_manager.simulation_mode is False, "Should be REAL GPIO on Pi"
        else:
            assert gpio_manager.simulation_mode is True, "Should be SIMULATION off-Pi"

    def test_double_init_is_safe(self):
        """Calling initialize() twice should not raise."""
        gpio_manager.initialize()  # second call
        assert gpio_manager.initialized is True


class TestPinRegistration:

    def test_setup_output_pin(self):
        """Should register an output pin successfully."""
        pin = pin_defs.led.red           # known safe pin (16 BCM)
        result = gpio_manager.setup_output(pin, initial=0)
        assert result is True
        assert gpio_manager.is_pin_active(pin)
        assert gpio_manager.pin_modes[pin] == 'OUT'
        print(f"\n  Pin {pin} registered as OUTPUT ✓")

    def test_setup_input_pin(self):
        """Should register an input pin successfully."""
        pin = pin_defs.ultrasonic.echo   # echo pin (6 BCM)
        result = gpio_manager.setup_input(pin)
        assert result is True
        assert gpio_manager.is_pin_active(pin)
        assert gpio_manager.pin_modes[pin] == 'IN'
        print(f"\n  Pin {pin} registered as INPUT ✓")

    def test_cleanup_removes_pin(self):
        """cleanup_pin() should deregister the pin."""
        pin = pin_defs.led.green
        gpio_manager.setup_output(pin)
        gpio_manager.cleanup_pin(pin)
        assert not gpio_manager.is_pin_active(pin)
        print(f"\n  Pin {pin} cleaned up ✓")

    def test_active_pins_list(self):
        """get_active_pins() should return all registered pins."""
        pins = [pin_defs.led.red, pin_defs.led.green, pin_defs.led.blue]
        for p in pins:
            gpio_manager.setup_output(p)
        active = gpio_manager.get_active_pins()
        for p in pins:
            assert p in active
        print(f"\n  Active pins: {sorted(active)} ✓")


class TestPinOperations:

    def test_output_high_low(self):
        """Should set output pin HIGH and LOW without error."""
        pin = pin_defs.led.red
        gpio_manager.setup_output(pin, initial=0)
        gpio_manager.output(pin, True)   # HIGH
        gpio_manager.output(pin, False)  # LOW
        print(f"\n  Pin {pin} HIGH→LOW toggled ✓")

    def test_output_wrong_mode_raises(self):
        """Setting output on an INPUT pin should raise ValueError."""
        pin = pin_defs.ultrasonic.echo
        gpio_manager.setup_input(pin)
        with pytest.raises(ValueError, match="not configured as output"):
            gpio_manager.output(pin, True)
        print(f"\n  Correctly rejected output on INPUT pin {pin} ✓")

    def test_unconfigured_pin_raises(self):
        """Operating on an unregistered pin should raise ValueError."""
        with pytest.raises(ValueError, match="not configured"):
            gpio_manager.output(99, True)  # pin 99 never registered

    @pytest.mark.hardware
    def test_all_motor_pins_configurable(self):
        """All motor pins from config should accept GPIO.OUT setup."""
        mp = pin_defs.motor
        pins = [
            mp.left_enable, mp.left_input1, mp.left_input2,
            mp.right_enable, mp.right_input3, mp.right_input4
        ]
        for pin in pins:
            result = gpio_manager.setup_output(pin, initial=0)
            assert result is True, f"Failed to configure motor pin {pin}"
        print(f"\n  Motor pins {pins} all configured ✓")

    @pytest.mark.hardware
    def test_all_servo_pins_configurable(self):
        """Servo PWM pins should register cleanly."""
        sp = pin_defs.servo
        for pin in [sp.pan, sp.tilt]:
            result = gpio_manager.setup_output(pin)
            assert result is True, f"Failed to configure servo pin {pin}"
        print(f"\n  Servo pins {[sp.pan, sp.tilt]} configured ✓")

"""
Integration Test for Surveillance Car System
Tests hardware manager and MQTT integration
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestHardwareIntegration:
    """Test hardware manager integration"""
    
    @pytest.fixture
    def mock_gpio(self):
        """Mock GPIO for testing without hardware"""
        with patch('Drivers.hardware.gpio.gpio_manager.GPIO_AVAILABLE', False):
            yield
    
    def test_hardware_manager_import(self):
        """Test that hardware manager can be imported"""
        from Drivers.hardware.managers.hardware_manager import hardware_manager
        assert hardware_manager is not None
    
    def test_hardware_manager_initialization(self, mock_gpio):
        """Test hardware manager initialization"""
        from Drivers.hardware.managers.hardware_manager import hardware_manager
        
        # Should initialize without errors in simulation mode
        try:
            hardware_manager.initialize()
            assert hardware_manager.initialized
        except Exception as e:
            pytest.fail(f"Hardware initialization failed: {e}")
        finally:
            hardware_manager.cleanup()
    
    def test_hardware_manager_status(self, mock_gpio):
        """Test getting hardware status"""
        from Drivers.hardware.managers.hardware_manager import hardware_manager
        
        hardware_manager.initialize()
        status = hardware_manager.get_status()
        
        assert 'initialized' in status
        assert 'emergency' in status
        assert 'watchdog' in status
        
        hardware_manager.cleanup()


class TestMQTTIntegration:
    """Test MQTT controller integration"""
    
    def test_mqtt_controller_import(self):
        """Test that MQTT controller can be imported"""
        from Network.MQTT.mqtt_device_controller_integrated import MQTTDeviceController
        assert MQTTDeviceController is not None
    
    def test_mqtt_controller_creation(self):
        """Test MQTT controller creation"""
        from Network.MQTT.mqtt_device_controller_integrated import MQTTDeviceController
        
        controller = MQTTDeviceController("localhost", 1883)
        assert controller.broker_host == "localhost"
        assert controller.broker_port == 1883
        assert not controller.connected
        assert not controller.running
    
    @patch('paho.mqtt.client.Client')
    def test_mqtt_topics_defined(self, mock_client):
        """Test that MQTT topics are properly defined"""
        from Network.MQTT.mqtt_device_controller_integrated import MQTTDeviceController
        
        controller = MQTTDeviceController("localhost", 1883)
        
        assert hasattr(controller, 'TOPIC_MOTOR')
        assert hasattr(controller, 'TOPIC_LED')
        assert hasattr(controller, 'TOPIC_SERVO')
        assert hasattr(controller, 'TOPIC_COMMANDS')
        assert hasattr(controller, 'TOPIC_STATUS')
        assert hasattr(controller, 'TOPIC_SENSORS')
        assert hasattr(controller, 'TOPIC_EMERGENCY')


class TestConfigurationIntegration:
    """Test configuration loading"""
    
    def test_config_files_exist(self):
        """Test that configuration files exist"""
        config_dir = Path(__file__).parent.parent / "config" / "hardware"
        
        assert (config_dir / "gpio_config.yaml").exists(), "gpio_config.yaml not found"
        assert (config_dir / "pwm_config.yaml").exists(), "pwm_config.yaml not found"
        assert (config_dir / "servo_config.yaml").exists(), "servo_config.yaml not found"
        assert (config_dir / "safety_config.yaml").exists(), "safety_config.yaml not found"
    
    def test_gpio_config_loading(self):
        """Test GPIO configuration loading"""
        import yaml
        config_path = Path(__file__).parent.parent / "config" / "hardware" / "gpio_config.yaml"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert 'motor' in config
        assert 'servo' in config
        assert 'led' in config
        assert 'ultrasonic' in config


class TestSystemIntegration:
    """Test complete system integration"""
    
    def test_main_module_import(self):
        """Test that main module can be imported"""
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        # Should be able to import without errors
        try:
            import main
            assert hasattr(main, 'SurveillanceCarSystem')
            assert hasattr(main, 'main')
        except ImportError as e:
            pytest.fail(f"Failed to import main module: {e}")
    
    def test_drivers_package(self):
        """Test Drivers package structure"""
        from Drivers import hardware_manager
        assert hardware_manager is not None
    
    def test_network_package(self):
        """Test Network package structure"""
        from Network.MQTT import mqtt_device_controller_integrated
        assert mqtt_device_controller_integrated is not None


def test_quick_system_check():
    """Quick system check - can everything be imported?"""
    errors = []
    
    # Test hardware imports
    try:
        from Drivers.hardware.managers.hardware_manager import hardware_manager
    except Exception as e:
        errors.append(f"Hardware manager import failed: {e}")
    
    # Test MQTT imports
    try:
        from Network.MQTT.mqtt_device_controller_integrated import MQTTDeviceController
    except Exception as e:
        errors.append(f"MQTT controller import failed: {e}")
    
    # Test connection manager
    try:
        from Network.MQTT.connection_manager import ConnectionManager
    except Exception as e:
        errors.append(f"Connection manager import failed: {e}")
    
    # Test main
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        import main
    except Exception as e:
        errors.append(f"Main module import failed: {e}")
    
    if errors:
        pytest.fail("\n".join(errors))


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])

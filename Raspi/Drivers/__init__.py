"""
Hardware Drivers Package
Provides hardware abstraction layer for the surveillance car
"""

from .hardware.managers.hardware_manager import hardware_manager

__all__ = ['hardware_manager']

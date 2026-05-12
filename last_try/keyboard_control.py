#!/usr/bin/env python3
"""
Simple Keyboard Control
Use arrow keys to control the car
"""
import sys
import tty
import termios
sys.path.insert(0, 'hardware')

from motor import Motor
from led import LED

def get_key():
    """Get a single keypress"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    print("=" * 50)
    print("Keyboard Control")
    print("=" * 50)
    print("\nControls:")
    print("  w = Forward")
    print("  s = Backward")
    print("  a = Left")
    print("  d = Right")
    print("  x = Stop")
    print("  q = Quit")
    print("\nPress any key to start...")
    
    motor = Motor()
    led = LED()
    
    try:
        motor.setup()
        led.setup()
        led.set_color(0, 255, 0)  # Green = ready
        
        print("\nReady! Use WASD keys to control")
        
        while True:
            key = get_key()
            
            if key == 'w':
                motor.forward(70)
                led.set_color(0, 0, 255)  # Blue = moving
            elif key == 's':
                motor.backward(70)
                led.set_color(255, 255, 0)  # Yellow = backward
            elif key == 'a':
                motor.left(70)
                led.set_color(255, 0, 255)  # Magenta = left
            elif key == 'd':
                motor.right(70)
                led.set_color(0, 255, 255)  # Cyan = right
            elif key == 'x':
                motor.stop()
                led.set_color(0, 255, 0)  # Green = stopped
            elif key == 'q':
                print("\nQuitting...")
                break
            elif key == '\x03':  # Ctrl+C
                break
                
    except KeyboardInterrupt:
        print("\n\nInterrupted")
    finally:
        motor.stop()
        led.off()
        motor.cleanup()
        led.cleanup()
        print("Cleanup done")

if __name__ == "__main__":
    main()

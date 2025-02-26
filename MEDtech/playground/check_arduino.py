from datetime import datetime
import serial
import time
import requests
from scipy.signal import find_peaks

# Configuration for Arduino connection
port = "COM3"  # Replace with your Arduino port (e.g., COM3 or /dev/ttyUSB0)
baud_rate = 9600
sampling_rate = 100  # Hz
window_size = sampling_rate * 5  # 5 seconds of data

# Flask backend URL
flask_url = "http://127.0.0.1:5000/api/save_bpm"
ser = None

def connect_arduino():
    """Connects to the Arduino."""
    global ser
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)  # Wait for the connection to stabilize
        print("Arduino connected successfully.")
    except Exception as e:
        print(f"Error connecting to Arduino: {e}")
if __name__ == '__main__':
    connect_arduino()
# connection.py
import serial
import time

class ArduinoConnection:
    def __init__(self, port="COM3", baud_rate=9600):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Wait for the connection to establish
            print("Arduino connected successfully.")
        except Exception as e:
            print(f"Error connecting to Arduino: {e}")
            self.ser = None

    def read_data(self):
        if self.ser and self.ser.is_open:
            try:
                raw_data = self.ser.readline().decode('utf-8').strip()
                return raw_data
            except Exception as e:
                print(f"Error reading data from Arduino: {e}")
                return None
        else:
            print("Arduino is not connected.")
            return None

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Arduino connection closed.")

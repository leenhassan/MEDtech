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
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)  # Wait for the connection to stabilize
        print("Arduino connected successfully.")
    except Exception as e:
        print(f"Error connecting to Arduino: {e}")
    

def send_start_signal_to_arduino():
    """Sends a 'start' signal to the Arduino."""
    if ser and ser.is_open:
        ser.write(b"start\n")
        print("Start signal sent to Arduino.")

def read_from_arduino():
    """Reads and prints heart rate data from Arduino."""
    try:
        if not ser or not ser.is_open:
            connect_arduino()

        while True:
            raw_data = ser.readline()  # Read a line of data
            try:
                decoded_data = raw_data.decode('utf-8').strip()  # Decode the data
                if decoded_data.isdigit():  # Check if the data is a valid number
                    heart_rate = int(decoded_data)
                    print(f"Heart rate: {heart_rate}")
                else:
                    print(f"Invalid data received: {decoded_data}")
            except UnicodeDecodeError as e:
                print(f"Error decoding data: {e} | Raw data: {raw_data}")
    except Exception as e:
        print(f"Error reading from Arduino: {e}")

def send_stop_signal_to_arduino():
    """Sends a 'stop' signal to the Arduino."""
    if ser and ser.is_open:
        ser.write(b"stop\n")
        print("Stop signal sent to Arduino.")

def send_bpm_to_backend(patient_id, bpm, timestamp):
    """Sends the calculated BPM to the Flask backend."""
    try:
        response = requests.post(
            flask_url,
            json={"patient_id": patient_id, "bpm": bpm, "timestamp": timestamp},
        )
        if response.status_code == 200:
            print(f"Successfully saved BPM: {bpm} for patient {patient_id}")
        else:
            print(f"Failed to save BPM: {response.json()}")
    except Exception as e:
        print(f"Error sending BPM to backend: {e}")

def read_heart_rate(patient_id):
    """Reads data from the Arduino, calculates BPM, and sends it to the backend."""
    global ser
    if not ser or not ser.is_open:
        connect_arduino()

    data_buffer = []
    try:
        while True:
            if ser.in_waiting > 0:
                try:
                    raw_data = ser.readline()  # Read a line of data
                    decoded_data = raw_data.decode('utf-8').strip()  # Decode the data
                    if decoded_data.isdigit():  # Validate numeric data
                        data_point = int(decoded_data)
                        data_buffer.append(data_point)

                        # Maintain a fixed buffer size
                        if len(data_buffer) > window_size:
                            data_buffer.pop(0)

                        # If the buffer is full, calculate BPM
                        if len(data_buffer) == window_size:
                            peaks, _ = find_peaks(data_buffer, distance=sampling_rate / 2)
                            bpm = len(peaks) * (60 / (len(data_buffer) / sampling_rate))
                            print(f"Calculated BPM: {bpm}")
                            send_bpm_to_backend(patient_id, bpm, datetime.now())
                    else:
                        print(f"Invalid data received: {decoded_data}")
                except UnicodeDecodeError as e:
                    print(f"Error decoding data: {e} | Raw data: {raw_data}")
    except Exception as e:
        print(f"Error reading heart rate: {e}")

    finally:
        if ser:
            ser.close()
            print("Arduino connection closed.")

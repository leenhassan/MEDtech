import serial
import time

class BPMCalculator:
    """
    A basic BPM calculator class that:
      - Receives ECG sample values,
      - Detects peaks based on a simple threshold,
      - Calculates BPM from time intervals between peaks.
    """

    def __init__(self, threshold=500, min_peak_interval=0.3):
        """
        :param threshold: The threshold used to detect a peak in the ECG signal.
        :param min_peak_interval: Minimum time (in seconds) between two valid peaks (refractory period).
        """
        self.threshold = threshold
        self.min_peak_interval = min_peak_interval

        # Track the time of the last detected R-peak
        self.last_peak_time = None

        # Current BPM (can be updated after each new peak is detected)
        self.current_bpm = 0

        # A flag to ensure we only detect a peak once 
        # when the value first exceeds the threshold.
        self.peak_detected = False

    def process_sample(self, ecg_value, current_time):
        """
        Process a single ECG sample.

        :param ecg_value: The ECG value (e.g. from AD8232) at this time instant.
        :param current_time: The time (in seconds) since the start of measurement (or an absolute timestamp).
        """
        # Check if signal goes above threshold and a peak hasn't already been flagged
        if ecg_value > self.threshold and not self.peak_detected:
            # We suspect a new peak if enough time has passed since last peak
            if (self.last_peak_time is None) or ((current_time - self.last_peak_time) >= self.min_peak_interval):
                # Calculate BPM if we have a previous peak time
                if self.last_peak_time is not None:
                    peak_interval = current_time - self.last_peak_time
                    # Instantaneous BPM = 60 / seconds per beat
                    self.current_bpm = 60.0 / peak_interval

                # Update the last peak time and set the peak_detected flag
                self.last_peak_time = current_time

            # Set peak_detected so we don’t repeatedly detect the same peak
            self.peak_detected = True

        # If the ecg_value goes below threshold, reset peak_detected
        elif ecg_value < self.threshold and self.peak_detected:
            self.peak_detected = False

    def get_bpm(self):
        """Return the most recent BPM value computed."""
        return self.current_bpm

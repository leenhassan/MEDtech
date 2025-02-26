import io
import threading
from flask import Blueprint, abort, app, render_template, request, redirect, url_for, flash, current_app, session, jsonify, send_file
from app.arduino.bpm_calculator import BPMCalculator
from app.models import Appointment, db, Patient, HeartRateData # Import your models
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import generate_verification_token, send_verification_email, confirm_verification_token
import os
import logging
from flask_mail import Message
from app import mail
from datetime import datetime, timedelta
import serial
import time
from app.arduino.connection import ArduinoConnection
from threading import Thread
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

main = Blueprint('main', __name__)
arduino_connection = ArduinoConnection(port="COM3", baud_rate=9600)
arduino_connection.connect() 

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

    
@main.route("/")
def home():
    return render_template("index.html")

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get form data
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        age = request.form.get("age")
        weight = request.form.get("weight")
        height = request.form.get("height")
        email = request.form.get("email")
        password = request.form.get("password")
        doctor_email = request.form.get("doctor_email")

        # Validate required fields
        if not all([first_name, last_name, age, weight, height, email, password, doctor_email]):
            flash("All fields are required.", "danger")
            return redirect(url_for("main.register"))

        # Check if email already exists
        if Patient.query.filter_by(email=email).first():
            flash("Email is already registered. Please use a different email.", "danger")
            return redirect(url_for("main.register"))

        # Create and save new patient
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_patient = Patient(
            first_name=first_name,
            last_name=last_name,
            age=int(age),
            weight=float(weight),
            height=float(height),
            email=email,
            password=hashed_password,
            doctor_email=doctor_email,
        )
        db.session.add(new_patient)
        db.session.commit()

        # Send verification email
        token = generate_verification_token(email)
        verification_url = url_for("main.verify_email", token=token, _external=True)
        send_verification_email(email, verification_url)

        flash("Registration successful! Please check your email for verification.", "success")
        return redirect(url_for("main.verification_sent"))

    return render_template("register.html")

@main.route("/verify_email/<token>")
def verify_email(token):
    try:
        email = confirm_verification_token(token)
        if not email:
            flash("The verification link is invalid or has expired.", "danger")
            return redirect(url_for("main.register"))

        patient = Patient.query.filter_by(email=email).first()
        if patient:
            patient.verified = True
            db.session.commit()
            flash("Your email has been verified! You can now log in.", "success")
            return redirect(url_for("main.login"))
        else:
            flash("Patient not found.", "danger")
            return redirect(url_for("main.register"))
    except Exception as e:
        flash("An error occurred during email verification. Please try again.", "danger")
        return redirect(url_for("main.register"))

@main.route("/verification_sent")
def verification_sent():
    return render_template("verification_sent.html")

@main.route("/verification_error")
def verification_error():
    return render_template("verification_error.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Find patient by email
        patient = Patient.query.filter_by(email=email).first()

        if patient and check_password_hash(patient.password, password):
            if not patient.verified:
                flash("Please verify your email before logging in.", "warning")
                return redirect(url_for("main.login"))
            session['logged_in'] = True
            session['user_email'] = patient.email 
            session["patient_id"] = patient.id  # Save patient ID in session
            session['role'] = 'patient'  
            flash("Login successful!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("main.login"))

    return render_template("login.html")

@main.route("/dashboard")
def dashboard():
    if "patient_id" not in session:
        flash("Please log in to access the dashboard.", "danger")
        return redirect(url_for("main.login"))
    patient_id = session['patient_id']

    # Query alerts for abnormal BPM (below 60 or above 120)
    alerts = HeartRateData.query.filter(
        (HeartRateData.patient_id == patient_id) &
        ((HeartRateData.bpm < 60) | (HeartRateData.bpm > 120))
    ).order_by(HeartRateData.timestamp.desc()).all()

    return render_template('dashboard.html', patient_id=patient_id, alerts=alerts)

@main.route('/bpm_graph/<int:patient_id>')
def bpm_graph(patient_id):
    # Get the current time
    now = datetime.utcnow()

    # Define time ranges
    last_24_hours = now - timedelta(hours=24)
    last_week = now - timedelta(weeks=1)

    # Query data for the last 24 hours
    data_24h = HeartRateData.query.filter(
        HeartRateData.patient_id == patient_id,
        HeartRateData.timestamp >= last_24_hours,
          HeartRateData.timestamp <= now
    ).order_by(HeartRateData.timestamp).all()

    # Query data for the last week
    data_week = HeartRateData.query.filter(
        HeartRateData.patient_id == patient_id,
        HeartRateData.timestamp >= last_week,
        HeartRateData.timestamp <= now
    ).order_by(HeartRateData.timestamp).all()

    # Check if data exists
    if not data_24h and not data_week:
        return "No data available for this patient."

    # Create the figure and axes for two graphs


    # Create the figure and axes for two graphs
    fig, axs = plt.subplots(2, 1, figsize=(12, 10), sharex=False)

    # Plot last 24 hours graph
    if data_24h:
        timestamps_24h = [record.timestamp for record in data_24h]
        bpm_values_24h = [record.bpm for record in data_24h]
        axs[0].plot(timestamps_24h, bpm_values_24h, marker='o', linestyle='-', color='b', label='Last 24 Hours')
        axs[0].set_title('BPM Trend for Last 24 Hours')
        axs[0].set_xlabel('Time')
        axs[0].set_ylabel('BPM')
        axs[0].grid(True)
        axs[0].legend()

        # Format x-axis for last 24 hours with hours and minutes
        axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        axs[0].xaxis.set_major_locator(mdates.HourLocator(interval=2))  # Set major ticks every 2 hours
        axs[0].tick_params(axis='x', rotation=45) # Rotate x-axis labels for better readability
    else:
        axs[0].text(0.5, 0.5, 'No Data for Last 24 Hours', horizontalalignment='center', verticalalignment='center')

    # Plot last week graph
    if data_week:
        # average data per day
        timestamps_week = [record.timestamp for record in data_week]
        bpm_values_week = [record.bpm for record in data_week]
        # Calculate average BPM per day
        bpm_values_week = [sum(bpm_values_week[i:i+24])/24 for i in range(0, len(bpm_values_week), 24)]
        # get respective timestampes
        timestamps_week = [timestamps_week[i] for i in range(0, len(timestamps_week) - 1, 24)]
        axs[1].plot(timestamps_week, bpm_values_week, marker='o', linestyle='-', color='g', label='Last Week')
        axs[1].set_title('BPM Trend for Last Week')
        axs[1].set_xlabel('Time')
        axs[1].set_ylabel('BPM')
        axs[1].grid(True)
        axs[1].legend()

        # Format x-axis for last week with day-level granularity
        axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        axs[1].xaxis.set_major_locator(mdates.DayLocator())  # Set major ticks for each day
        axs[1].tick_params(axis='x', rotation=45) # Rotate x-axis labels for better readability
    else:
        axs[1].text(0.5, 0.5, 'No Data for Last Week', horizontalalignment='center', verticalalignment='center')

    # Save the graph to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()


    return send_file(img, mimetype='image/png')


@main.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    # Fetch the logged-in user's data using their email
    email = session.get('user_email')
    patient = Patient.query.filter_by(email=email).first()

    if not patient:
        flash("Patient data not found.", "error")
        return redirect(url_for('main.profile'))

    if request.method == 'POST':
        # Update patient data with form inputs
        patient.first_name = request.form['first_name']
        patient.last_name = request.form['last_name']
        patient.age = request.form['age']
        patient.weight = request.form['weight']
        patient.height = request.form['height']
        patient.doctor_email = request.form['doctor_email']

        try:
            db.session.commit()  # Save changes to the database
            flash("Profile updated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating the profile.", "error")
            print("Error:", e)

        return redirect(url_for('main.profile'))

    return render_template('edit_profile.html', patient=patient)


@main.route("/logout")
def logout():
    session.pop("patient_id", None)  # Remove patient ID from session
    flash("You have been logged out.", "success")
    return redirect(url_for("main.login"))

@main.route("/about")
def about():
    return render_template("about.html")


@main.route('/profile')
def profile():
    if "patient_id" not in session:
        flash("Please log in.", "danger")
        return redirect(url_for("main.login"))

    # Fetch the logged-in user's data using their email
    email = session.get('user_email')
    patient = Patient.query.filter_by(email=email).first()

    return render_template('profile.html', patient=patient)

@main.route('/schedule')
def calendar():
    if "patient_id" not in session:
        flash("Please log in to access your appointments.", "danger")
        return redirect(url_for("main.login"))

    return render_template("schedule.html")


@main.route('/appointments', methods=['GET'])
def get_appointments():
    # Retrieve the logged-in patient's ID from the session
    patient_id = session.get('patient_id')
    
    if not patient_id:
        abort(403)  # Return a 403 Forbidden response if patient_id is not set in the session

    # Parse the year and month from the request arguments
    year = request.args.get('year')
    month = request.args.get('month')
    
    if not year or not month:
        return jsonify({'error': 'Year and month are required parameters.'}), 400
    
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        return jsonify({'error': 'Year and month must be integers.'}), 400

    # Query the appointments for the logged-in patient for the specified year and month
    appointments = Appointment.query.filter(
        db.extract('year', Appointment.date) == year,
        db.extract('month', Appointment.date) == month,
        Appointment.patient_id == patient_id
    ).all()

    # Format and return the appointments as JSON
    return jsonify([{
        'id': a.id,
        'title': a.title,
        'day': a.date.day,
        'time': a.time.strftime('%H:%M') if a.time else None
    } for a in appointments])

@main.route('/add_appointment', methods=['POST'])
def add_appointment():
    # Ensure the user is logged in
    if 'patient_id' not in session or 'user_email' not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.json

    try:
        # Create a new appointment
        new_appointment = Appointment(
            patient_id=session.get('patient_id'),
            title=data['title'],
            date=datetime.strptime(f"{data['year']}-{data['month']}-{data['day']}", '%Y-%m-%d').date(),
            time=datetime.strptime(data['time'], '%H:%M').time(),
            email=session.get('user_email')  # Use the email from the session
        )
        db.session.add(new_appointment)
        db.session.commit()
        return jsonify({'message': 'Appointment added successfully'}), 201

    except KeyError as e:
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": f"Invalid date or time format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@main.route('/edit_appointment/<int:appointment_id>', methods=['POST'])
def edit_appointment(appointment_id):
    data = request.json
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        appointment.title = data['title']
        appointment.time = datetime.strptime(data['time'], '%H:%M').time()
        db.session.commit()
        return jsonify({'message': 'Appointment updated successfully'})
    return jsonify({'error': 'Appointment not found'}), 404

def send_email_reminder(appointment):
    with app.app_context():
        msg = Message("Appointment Reminder", sender="dija.aa1714@gmail.com", recipients=[appointment.email])
        msg.body = f"Reminder: You have an appointment '{appointment.title}' scheduled on {appointment.date} at {appointment.time}."
        mail.send(msg)


def check_for_appointments():
    with current_app.app_context():  # Bind the thread to the Flask app context
        try:
            today_start = datetime.now()
            appointments = Appointment.query.filter(Appointment.date == today_start.date()).all()

            for appointment in appointments:
                # Send reminder email logic
                print(f"Sending reminder for appointment: {appointment.title} at {appointment.time}")

        except Exception as e:
            print(f"Error in appointment checking thread: {e}")

# Start the thread
def start_checking_thread():
    app = current_app._get_current_object()  # Get the actual app object
    thread = threading.Thread(target=check_for_appointments)
    thread.daemon = True  # Allows the program to exit even if the thread is running
    with app.app_context():
        thread.start()



@main.route('/game')
def game():
    return render_template('game.html')

@main.route('/start_recording', methods=['POST'])
def start_recording():
    print("session:", session.get('patient_id'))
    
    # Ensure the user is logged in
    if 'patient_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    patient_id = session['patient_id']  # Get logged-in patient ID
    bpm = None
    current_time = None

    bpm_calculator = BPMCalculator(threshold=500, min_peak_interval=0.3)

    start_time = time.time()

    try:
        while True:
            line = arduino_connection.read_data()
            if line:
                try:
                    # Convert the serial string to a float (ECG voltage or ADC value)
                    ecg_value = float(line)
                    print(f"ecg_value: {ecg_value}")

                    # Calculate elapsed time since start
                    current_time = time.time() - start_time

                    # Process the ECG sample
                    bpm_calculator.process_sample(ecg_value, current_time)

                    # Retrieve the latest BPM
                    bpm = bpm_calculator.get_bpm()
                    print("bpm", bpm)

                    # Print or log it
                    print(f"ECG Value: {ecg_value:.2f}, BPM: {bpm:.2f}")

                except ValueError:
                    # Handle any parse errors
                    pass

    except KeyboardInterrupt:
        print("Stopped by user.")
    
    if bpm is None:
        print("Error: BPM value is None. Skipping database insert.")
    else:
        heart_rate_data = HeartRateData(
            patient_id=patient_id,
            bpm=bpm,
            timestamp=current_time
        )
        db.session.add(heart_rate_data)
        db.session.commit()
        print(f"BPM data saved successfully: {bpm} for patient {patient_id}")



@main.route('/stop_recording', methods=['POST'])
def stop_recording():
    if 'patient_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    try:
        arduino_connection.close()
        return jsonify({"message": "Recording stopped"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/api/save_bpm', methods=['POST'])
def save_bpm():
    try:
        print(f"Received data: {request.json}")
        patient_id = request.json.get('patient_id')
        bpm = request.json.get('bpm')
        timestamp = request.json.get('timestamp')

        if not patient_id or not bpm:
            print("Invalid data received.")
            return jsonify({"error": "Invalid data"}), 400

        # Save BPM to the database
        heart_rate_data = HeartRateData(
            patient_id=patient_id,
            bpm=bpm,
            timestamp=datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')  # Convert timestamp to datetime object
        )
        db.session.add(heart_rate_data)
        db.session.commit()
        print(f"BPM data saved successfully: {bpm} for patient {patient_id}")
        return jsonify({"message": "BPM data saved successfully"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500




# Ensure the upload directory exists
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Delete Patient route

@main.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # Collect form data
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        
        # Validate and process the data
        if not name or not email or not message:
            flash("All fields are required!", "danger")
            return redirect(url_for("main.contact"))
        
        # Send email using Flask-Mail
        try:
            msg = Message(
                subject=f"New Contact Form Submission from {name}",
                sender=email,
                recipients=["dija.aa1714@gmail.com"],  # Replace with your receiving email
                body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            )
            mail.send(msg)
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            print(f"Error sending email: {e}")
            flash("There was an error sending your message. Please try again later.", "danger")
            return redirect(url_for("main.contact"))
        
        return redirect(url_for("main.contact"))

    # Render the contact page
    return render_template("contact.html")

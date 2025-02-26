# MEDTech Future 🚀
MEDTech Future is an advanced web application designed for heart rate monitoring, patient management, and interactive CPR training. It provides real-time health insights, appointment scheduling, and emergency alerts, ensuring better healthcare monitoring and safety.

---

## 🔹 Features  

### 🔑 User Authentication & Security  
✔️ Secure user registration & login system.  
✔️ Email verification for account activation.  
✔️ Role-based access (patients & doctors).  

### 📅 Appointment Scheduling  
✔️ Interactive calendar for managing appointments.  
✔️ Time-based scheduling to avoid conflicts.  
✔️ Automatic email reminders for upcoming appointments.  

### ❤️ Heart Rate Monitoring  
✔️ Live data processing from **Arduino ECG Heart Rate Monitor (AD8232)**.  
✔️ Real-time storage & analysis of heart rate trends.  
✔️ Irregular heartbeat alerts for potential emergencies.  

### 🎮 Interactive CPR Training Game  
✔️ Learn CPR timing through an engaging interactive game.  
✔️ Feedback on click pace to match proper CPR rhythm.  
✔️ Multiple songs with BPM settings for realistic practice.  

### 📊 Health Insights Dashboard  
✔️ Graphical reports for heart rate trends (daily/weekly).  
✔️ Alerts for abnormal readings detected by the system.  
✔️ Personalized insights for patient health monitoring.  

### 🏥 Admin & Doctor Dashboard  
✔️ Manage patient profiles, medical history, & schedules.  
✔️ Full access to patient records & heart rate data.  
✔️ Integrated patient database management for easy tracking.  

---

## 🛠️ Tech Stack  

### 🌐 Frontend  
🔹 **HTML5, CSS3** *(Bootstrap for responsiveness)*.  
🔹 **JavaScript** *(Interactive UI, Calendar, and Game Logic)*.  
🔹 **Undraw Illustrations & Animate.css** *(for modern visuals)*.  

### 🖥️ Backend  
🔹 **Flask (Python)** for web application development.  
🔹 **Flask-Mail** for sending **email alerts & notifications**.  
🔹 **Flask-SQLAlchemy** for **database management**.  

### 🗄️ Database  
🔹 **MySQL** *(stores users, appointments, & heart rate data)*.  
🔹 **SQLAlchemy ORM** *(efficient database operations)*.  

### 🔌 Hardware Integration  
🔹 **Arduino ECG Heart Rate Monitor AD8232** *(real-time monitoring)*.  
🔹 **Serial communication for data processing**.  

---

## 📥 Installation Guide  

### 📌 Prerequisites  
✔️ **Python 3.9+**  
✔️ **MySQL (for database management)**  
✔️ **Arduino ECG Heart Rate Monitor AD8232** *(optional for hardware-based monitoring features)*  

---

### ⚙️ Steps to Set Up the Project  

#### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/leenhassan/MEDtech.git
cd MEDtech

2️⃣ Set Up a Virtual Environment (Recommended)

python -m venv env
source env/bin/activate  # For macOS/Linux
env\Scripts\activate  # For Windows

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Set Up Database

python generate_dummy_data.py  # Populate database with test data

5️⃣ Run the Application

python run.py

6️⃣ Open in Browser

http://localhost:5000
📂 Project Structure
MEDtech/
├── app/
│   ├── static/
│   ├── templates/
│   ├── models.py
│   ├── routes.py
│   ├── utils.py
├── migrations/
├── database.db
├── run.py
├── requirements.txt
└── README.md



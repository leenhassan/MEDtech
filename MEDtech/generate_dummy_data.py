import random
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.models import HeartRateData




Base = declarative_base()

# Database setup (replace with your actual database URL)
DATABASE_URL = 'mysql+pymysql://root:Khadija2005*@localhost/medtech_db'  # Use SQLite for simplicity
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def generate_dummy_data_batch():
    patients = [1, 2]  # Patient IDs
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    n_minutes_per_day = 120

    batch_size = 1000  # Adjust batch size for optimal performance
    batch = []
    for patient_id in patients:
        current_date = start_date
        while current_date <= end_date:
            for minute in range(0, n_minutes_per_day, 1):  # 1440 minutes in a day
                if minute % 2 == 0:  # Interleaved by a day (every other minute is skipped)
                    bpm = random.uniform(60, 100)  # Random BPM between 60 and 100
                    timestamp = current_date + timedelta(minutes=minute)
                    data = HeartRateData(patient_id=patient_id, bpm=bpm, timestamp=timestamp)
                    batch.append(data)
                    
                    if len(batch) >= batch_size:
                        session.bulk_save_objects(batch)
                        session.commit()
                        batch = []  # Clear the batch
            
            current_date += timedelta(days=2)  # Skip to the next interleaved day
    
    # Commit any remaining records in the batch
    if batch:
        session.bulk_save_objects(batch)
        session.commit()
    
    print("Dummy data generation complete!")


# Run the data generation
generate_dummy_data_batch()

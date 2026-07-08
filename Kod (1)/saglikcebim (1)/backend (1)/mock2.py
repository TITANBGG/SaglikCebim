import sys
import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.getcwd())
from app.core.database import Base
from app.models.user import User
from app.models.anamnesis import PatientProfile
from app.models.patient_conditions import PatientCondition
from app.models.patient_allergies import PatientAllergy

# Drop old tables
conn = sqlite3.connect('dev.db')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS patient_conditions')
cursor.execute('DROP TABLE IF EXISTS patient_allergies')
conn.commit()
conn.close()

engine = create_engine('sqlite:///./dev.db')
PatientCondition.__table__.create(engine)
PatientAllergy.__table__.create(engine)

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

user = db.query(User).filter(User.email.ilike('%alinebierr%')).first()

# Anamnesis Profile
profile = db.query(PatientProfile).filter(PatientProfile.user_id == user.id).first()
if not profile:
    profile = PatientProfile(user_id=user.id)
    db.add(profile)
profile.gender = 'Erkek'
profile.blood_type = 'A+'
profile.height = '180'
profile.weight = '85'
profile.age = '28'

# Conditions
db.query(PatientCondition).filter(PatientCondition.user_id == user.id).delete()
c1 = PatientCondition(user_id=user.id, condition_name='Hipertansiyon', diagnosis_date='2020-01-01')
c2 = PatientCondition(user_id=user.id, condition_name='Astım', diagnosis_date='2015-06-01')
db.add_all([c1, c2])

# Allergies
db.query(PatientAllergy).filter(PatientAllergy.user_id == user.id).delete()
a1 = PatientAllergy(user_id=user.id, allergen_name='Penisilin', reaction_type='Yüksek')
a2 = PatientAllergy(user_id=user.id, allergen_name='Polen', reaction_type='Orta')
db.add_all([a1, a2])

db.commit()
print('Profile injected successfully!')

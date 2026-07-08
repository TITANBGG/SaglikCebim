from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.anamnesis import PatientProfile
from app.models.patient_conditions import PatientCondition
from app.models.patient_medications import PatientMedication
from app.models.patient_allergies import PatientAllergy

router = APIRouter()

# --- Pydantic Schemas ---

class ProfileSchema(BaseModel):
    age: str | None = None
    gender: str | None = None
    height: str | None = None
    weight: str | None = None
    blood_type: str | None = None

class ConditionSchema(BaseModel):
    condition_name: str
    diagnosis_date: str | None = None

class MedicationSchema(BaseModel):
    medication_name: str
    dosage: str | None = None
    start_date: str | None = None

class PharmacyCheckSchema(BaseModel):
    substance_name: str

class AllergySchema(BaseModel):
    allergen_name: str
    reaction_type: str | None = None


# --- 1. PATIENT PROFILE ---
@router.get("/profile")
def get_profile(current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user_id).first()
    if not profile:
        return {}
    return {
        "id": str(profile.id),
        "age": profile.age,
        "gender": profile.gender,
        "height": profile.height,
        "weight": profile.weight,
        "blood_type": profile.blood_type
    }

@router.put("/profile")
def update_profile(data: ProfileSchema, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user_id).first()
    if not profile:
        profile = PatientProfile(user_id=current_user_id)
        db.add(profile)
    
    if data.age is not None: profile.age = data.age
    if data.gender is not None: profile.gender = data.gender
    if data.height is not None: profile.height = data.height
    if data.weight is not None: profile.weight = data.weight
    if data.blood_type is not None: profile.blood_type = data.blood_type
    
    db.commit()
    return {"status": "success", "message": "Profile updated successfully"}


# --- 2. PATIENT CONDITIONS (Diagnosis Agent Feeder) ---
@router.get("/conditions")
def get_conditions(current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(PatientCondition).filter(PatientCondition.user_id == current_user_id).all()
    return [{"id": str(i.id), "condition_name": i.condition_name, "diagnosis_date": i.diagnosis_date} for i in items]

@router.post("/conditions")
def add_condition(data: ConditionSchema, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    new_item = PatientCondition(
        user_id=current_user_id,
        condition_name=data.condition_name,
        diagnosis_date=data.diagnosis_date
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"id": str(new_item.id), "status": "success"}

@router.delete("/conditions/{item_id}")
def delete_condition(item_id: str, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(PatientCondition).filter(PatientCondition.id == item_id, PatientCondition.user_id == current_user_id).first()
    if item:
        db.delete(item)
        db.commit()
    return {"status": "success"}


# --- 3. PATIENT MEDICATIONS (Pharmacology Agent Feeder) ---
@router.get("/medications")
def get_medications(current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(PatientMedication).filter(PatientMedication.user_id == current_user_id).all()
    return [{"id": str(i.id), "medication_name": i.medication_name, "dosage": i.dosage, "start_date": i.start_date} for i in items]

@router.post("/medications")
def add_medication(data: MedicationSchema, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    new_item = PatientMedication(
        user_id=current_user_id,
        medication_name=data.medication_name,
        dosage=data.dosage,
        start_date=data.start_date
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"id": str(new_item.id), "status": "success"}

@router.delete("/medications/{item_id}")
def delete_medication(item_id: str, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(PatientMedication).filter(PatientMedication.id == item_id, PatientMedication.user_id == current_user_id).first()
    if item:
        db.delete(item)
        db.commit()
    return {"status": "success"}

@router.post("/pharmacy-check")
def pharmacy_check(data: PharmacyCheckSchema, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.services.clinical.pharmacology_agent import PharmacologyAgent

    items = db.query(PatientMedication).filter(PatientMedication.user_id == current_user_id).all()
    current_meds = [i.medication_name for i in items]
    agent = PharmacologyAgent(current_meds)
    report = agent.check_new_substance(data.substance_name)

    return {
        "status": "risk" if report.get("has_risk") else "clear",
        "checked_substance": data.substance_name,
        "current_medications": current_meds,
        "risks": [report.get("message", "")] if report.get("has_risk") else [],
        "severity": report.get("severity", "none"),
        "details": report.get("details", ""),
        "message": report.get("message", "Etkileşim kontrolü tamamlandı."),
    }


# --- 4. PATIENT ALLERGIES (Pharmacology Agent Feeder) ---
@router.get("/allergies")
def get_allergies(current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(PatientAllergy).filter(PatientAllergy.user_id == current_user_id).all()
    return [{"id": str(i.id), "allergen_name": i.allergen_name, "reaction_type": i.reaction_type} for i in items]

@router.post("/allergies")
def add_allergy(data: AllergySchema, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    new_item = PatientAllergy(
        user_id=current_user_id,
        allergen_name=data.allergen_name,
        reaction_type=data.reaction_type
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"id": str(new_item.id), "status": "success"}

@router.delete("/allergies/{item_id}")
def delete_allergy(item_id: str, current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(PatientAllergy).filter(PatientAllergy.id == item_id, PatientAllergy.user_id == current_user_id).first()
    if item:
        db.delete(item)
        db.commit()
    return {"status": "success"}

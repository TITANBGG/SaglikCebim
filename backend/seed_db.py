#!/usr/bin/env python
"""
Database seeding script - creates demo data for testing
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.report import Report
from app.models.test_result import TestResult
import uuid

def seed_database():
    """Create demo data"""
    init_db()
    db = SessionLocal()
    
    try:
        # Check if demo user exists
        demo_user = db.query(User).filter(User.email == "demo@example.com").first()
        
        if demo_user:
            print("✅ Demo user already exists")
            return
        
        # Create demo user
        demo_user = User(
            email="demo@example.com",
            hashed_password=get_password_hash("Demo123!@#"),
            full_name="Demo User"
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        print(f"✅ Created demo user (ID: {demo_user.id})")
        
        # Create sample reports
        sample_files = ["Kan_Tahlili.pdf", "Radyoloji_2024.pdf", "Biyokimya.pdf"]
        reports = []
        
        for i, filename in enumerate(sample_files):
            # SQLite doesn't support UUID properly, so we create without explicit id
            report = Report(
                user_id=demo_user.id,
                filename=f"{demo_user.id}_{i}_{filename}",
                original_filename=filename,
                file_path=f"uploads/{demo_user.id}_{i}_{filename}",
                status="analyzed",
                created_at=datetime.now() - timedelta(days=i)
            )
            db.add(report)
            db.flush()
            db.refresh(report)
            reports.append(report)
            print(f"✅ Created report: {filename} (ID: {report.id})")
        
        # Create sample test results
        sample_tests = [
            {"name": "Hemoglobin", "value": "14.5", "unit": "g/dL", "ref_min": "13.5", "ref_max": "17.5", "status": "Normal"},
            {"name": "WBC", "value": "7.2", "unit": "K/µL", "ref_min": "4.5", "ref_max": "11.0", "status": "Normal"},
            {"name": "Platelet", "value": "250", "unit": "K/µL", "ref_min": "150", "ref_max": "400", "status": "Normal"},
            {"name": "Glucose", "value": "105", "unit": "mg/dL", "ref_min": "70", "ref_max": "100", "status": "Abnormal"},
            {"name": "Cholesterol", "value": "220", "unit": "mg/dL", "ref_min": "0", "ref_max": "200", "status": "Abnormal"},
        ]
        
        if reports:
            for test_data in sample_tests:
                test_result = TestResult(
                    report_id=str(reports[0].id),
                    test_name=test_data["name"],
                    value=test_data["value"],
                    unit=test_data["unit"],
                    ref_min=float(test_data["ref_min"]),
                    ref_max=float(test_data["ref_max"]),
                    status=test_data["status"]
                )
                db.add(test_result)
                print(f"  └─ {test_data['name']}: {test_data['value']} {test_data['unit']} ({test_data['status']})")
            
            db.commit()
        
        print("\n✅ Database seeding completed!")
        print(f"Demo user: demo@example.com / Demo123!@#")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during seeding: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

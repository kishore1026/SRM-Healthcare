import sys
import os

# Add project directory to sys.path
sys.path.insert(0, r"c:\Users\HP\Desktop\srm_healthcare")

from app import create_app, db
from app.models.patient import Patient
from app.models.visit import PatientVisit
from app.models.medicine import Medicine

def check_database():
    app = create_app()
    with app.app_context():
        try:
            print("=========================================")
            print(" SRM HEALTHCARE - LOCAL DATABASE STATUS")
            print("=========================================")
            
            # Print connection URI
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            print(f"Connecting to: {db_uri.split('@')[-1] if '@' in db_uri else db_uri}")
            
            # Count records
            patient_count = Patient.query.count()
            visit_count = PatientVisit.query.count()
            medicine_count = Medicine.query.count()
            
            print(f"\nTotal Patients Registered : {patient_count}")
            print(f"Total Patient Visits      : {visit_count}")
            print(f"Total Medicines In Stock  : {medicine_count}")
            
            print("\n-----------------------------------------")
            print(" LATEST 5 REGISTERED PATIENTS:")
            print("-----------------------------------------")
            
            latest_patients = Patient.query.order_index_by = Patient.id.desc()
            latest_patients = Patient.query.order_by(Patient.id.desc()).limit(5).all()
            
            if not latest_patients:
                print("No patients registered yet in the database.")
            else:
                for idx, p in enumerate(latest_patients, 1):
                    hostel = p.hostel_name if p.hostel_name else "—"
                    room = p.room_number if p.room_number else "—"
                    sid = p.student_id if p.student_id else "—"
                    staff_id = p.staff_id if p.staff_id else "—"
                    
                    print(f"{idx}. {p.patient_name} (Age: {p.age}, Gender: {p.gender})")
                    print(f"   Designation: {p.designation}")
                    if p.designation == 'Student':
                        print(f"   Student ID : {sid} | Hostel: {hostel} | Room: {room}")
                    elif p.designation in ['Staff', 'Other']:
                        print(f"   ID Number  : {staff_id}")
                    print(f"   Registered : {p.created_at.strftime('%Y-%m-%d %H:%M:%S') if p.created_at else '—'}")
                    print()
            print("=========================================")
            
        except Exception as e:
            print(f"Error checking database: {e}")

if __name__ == '__main__':
    check_database()

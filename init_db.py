"""
Скрипт инициализации базы данных
Запуск: python -m init_db
"""

from server.database import init_db, engine, Base
from server.models import Staff, Patient, MedicalCard, Visit, Diagnosis, TreatmentPlan, Service, Equipment, Payment  # ← Добавьте все модели!
from server.database import SessionLocal
from server.auth import get_password_hash

def create_initial_data():
    """Создание начальных данных"""
    db = SessionLocal()
    
    try:
        # Проверка наличия администратора
        admin = db.query(Staff).filter(Staff.login_mis == "admin").first()
        
        if not admin:
            # Создание администратора
            admin = Staff(
                full_name="System Administrator",
                role="doctor",
                login_mis="admin",
                password_hash=get_password_hash("admin123"),
                specialization="Administration"
            )
            db.add(admin)
            
            # Создание тестового врача
            doctor = Staff(
                full_name="Dr. John Smith",
                role="doctor",
                login_mis="doctor1",
                password_hash=get_password_hash("doctor123"),
                specialization="Therapy"
            )
            db.add(doctor)
            
            # Создание регистратора
            registrar = Staff(
                full_name="Jane Doe",
                role="registrar",
                login_mis="registrar1",
                password_hash=get_password_hash("registrar123")
            )
            db.add(registrar)
            
            db.commit()
            print("✅ Начальные данные созданы успешно!")
            print("\n📝 Учетные данные:")
            print("  Admin: admin / admin123")
            print("  Doctor: doctor1 / doctor123")
            print("  Registrar: registrar1 / registrar123")
        else:
            print("ℹ️  Начальные данные уже существуют")
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Инициализация базы данных...")
    init_db()
    print("✅ Таблицы созданы")
    
    print("\n📝 Создание начальных данных...")
    create_initial_data()
    
    print("\n✨ Готово!")
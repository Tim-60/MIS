import pytest
from datetime import date
from server.repositories import (
    StaffRepository, 
    PatientRepository, 
    VisitRepository,
    DiagnosisRepository
)
from server.models import Staff, Patient, Visit, Diagnosis

class TestStaffRepository:
    """Тесты репозитория Staff"""
    
    def test_add_staff(self, db_session):
        """Тест добавления сотрудника"""
        repo = StaffRepository(db_session)
        
        staff = Staff(
            full_name="New Doctor",
            role="doctor",
            login_mis="new_doctor",
            password_hash="hashed_password"
        )
        
        result = repo.add(staff)
        assert result.staff_id is not None
        assert result.full_name == "New Doctor"
    
    def test_get_by_id(self, db_session, test_user):
        """Тест получения по ID"""
        repo = StaffRepository(db_session)
        result = repo.get_by_id(test_user.staff_id)
        
        assert result is not None
        assert result.staff_id == test_user.staff_id
        assert result.login_mis == "test_doctor"
    
    def test_update_staff(self, db_session, test_user):
        """Тест обновления сотрудника"""
        repo = StaffRepository(db_session)
        
        test_user.specialization = "Cardiology"
        result = repo.update(test_user)
        
        assert result.specialization == "Cardiology"
    
    def test_delete_staff(self, db_session, test_user):
        """Тест удаления сотрудника"""
        repo = StaffRepository(db_session)
        result = repo.delete(test_user.staff_id)
        
        assert result is True
        assert repo.get_by_id(test_user.staff_id) is None
    
    def test_find_staff(self, db_session, test_user):
        """Тест поиска сотрудников"""
        repo = StaffRepository(db_session)
        results = repo.find({"role": "doctor"})
        
        assert len(results) >= 1
        assert any(s.login_mis == "test_doctor" for s in results)
    
    def test_raw_sql_methods(self, db_session, test_user):
        """Тест SQL методов"""
        repo = StaffRepository(db_session)
        
        # Тест get_by_id_sql
        result = repo.get_by_id_sql(test_user.staff_id)
        assert result is not None
        assert result['login_mis'] == 'test_doctor'
        
        # Тест find_sql
        results = repo.find_sql({"role": "doctor"})
        assert len(results) >= 1

class TestPatientRepository:
    """Тесты репозитория Patient"""
    
    def test_add_patient(self, db_session):
        """Тест добавления пациента"""
        repo = PatientRepository(db_session)
        
        patient = Patient(
            full_name="John Doe",
            passport_data="1234 567890",
            birth_date=date(1990, 1, 1),
            phone="+1234567890"
        )
        
        result = repo.add(patient)
        assert result.patient_id is not None
        assert result.full_name == "John Doe"
    
    def test_find_by_name_sql(self, db_session):
        """Тест поиска по имени (SQL)"""
        repo = PatientRepository(db_session)
        
        # Создаем тестовых пациентов
        patient1 = Patient(
            full_name="John Smith",
            passport_data="1111 111111",
            birth_date=date(1985, 5, 15)
        )
        patient2 = Patient(
            full_name="Jane Smith",
            passport_data="2222 222222",
            birth_date=date(1992, 8, 20)
        )
        
        db_session.add(patient1)
        db_session.add(patient2)
        db_session.commit()
        
        results = repo.find_by_name_sql("Smith")
        assert len(results) == 2

class TestVisitRepository:
    """Тесты репозитория Visit"""
    
    def test_create_visit(self, db_session, test_user):
        """Тест создания визита"""
        # Сначала создаем пациента и карту
        patient = Patient(
            full_name="Test Patient",
            passport_data="9999 999999",
            birth_date=date(1980, 1, 1)
        )
        db_session.add(patient)
        db_session.commit()
        
        from server.models import MedicalCard
        card = MedicalCard(
            patient_id=patient.patient_id,
            registrar_id=test_user.staff_id
        )
        db_session.add(card)
        db_session.commit()
        
        # Создаем визит
        repo = VisitRepository(db_session)
        visit = Visit(
            card_id=card.card_id,
            doctor_id=test_user.staff_id,
            complaints="Headache"
        )
        
        result = repo.add(visit)
        assert result.visit_id is not None
        assert result.status == "in_progress"
    
    def test_update_status_sql(self, db_session, test_user):
        """Тест обновления статуса (SQL)"""
        # Создаем визит
        patient = Patient(
            full_name="Test Patient",
            passport_data="8888 888888",
            birth_date=date(1975, 3, 10)
        )
        db_session.add(patient)
        db_session.commit()
        
        from server.models import MedicalCard
        card = MedicalCard(
            patient_id=patient.patient_id,
            registrar_id=test_user.staff_id
        )
        db_session.add(card)
        db_session.commit()
        
        visit = Visit(
            card_id=card.card_id,
            doctor_id=test_user.staff_id
        )
        db_session.add(visit)
        db_session.commit()
        
        # Обновляем статус
        repo = VisitRepository(db_session)
        result = repo.update_status_sql(visit.visit_id, "completed")
        
        assert result is True
        
        # Проверяем обновление
        updated_visit = repo.get_by_id(visit.visit_id)
        assert updated_visit.status == "completed"

class TestDiagnosisRepository:
    """Тесты репозитория Diagnosis"""
    
    def test_add_diagnosis(self, db_session):
        """Тест добавления диагноза"""
        # Создаем тестовый визит
        patient = Patient(
            full_name="Patient for Diagnosis",
            passport_data="7777 777777",
            birth_date=date(1988, 12, 1)
        )
        db_session.add(patient)
        db_session.commit()
        
        from server.models import MedicalCard
        card = MedicalCard(
            patient_id=patient.patient_id,
            registrar_id=1
        )
        db_session.add(card)
        db_session.commit()
        
        visit = Visit(
            card_id=card.card_id,
            doctor_id=1
        )
        db_session.add(visit)
        db_session.commit()
        
        # Создаем диагноз
        repo = DiagnosisRepository(db_session)
        diagnosis = Diagnosis(
            visit_id=visit.visit_id,
            severity="moderate",
            description="Acute respiratory infection"
        )
        
        result = repo.add(diagnosis)
        assert result.diagnosis_id is not None
        assert result.severity == "moderate"
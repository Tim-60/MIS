import pytest
from fastapi.testclient import TestClient
from server.main import app
from server.database import get_db
import json

client = TestClient(app)

def test_health_check():
    """Тест проверки здоровья API"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_root_endpoint():
    """Тест корневого endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Medical Information System" in data["message"]

def test_create_patient(auth_headers, db_session):
    """Тест создания пациента через API"""
    patient_data = {
        "full_name": "API Test Patient",
        "passport_data": "5555 555555",
        "birth_date": "1995-06-15",
        "phone": "+79991234567",
        "address": "Test Street 123"
    }
    
    response = client.post(
        "/patients",
        json=patient_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "API Test Patient"
    assert data["passport_data"] == "5555 555555"

def test_get_patients(auth_headers):
    """Тест получения списка пациентов"""
    response = client.get("/patients", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_visit(auth_headers, db_session):
    """Тест создания визита через API"""
    # Создаем пациента и карту
    from server.models import Patient, MedicalCard
    from datetime import date
    
    patient = Patient(
        full_name="Visit Test Patient",
        passport_data="4444 444444",
        birth_date=date(1990, 1, 1)
    )
    db_session.add(patient)
    db_session.commit()
    
    card = MedicalCard(
        patient_id=patient.patient_id,
        registrar_id=1
    )
    db_session.add(card)
    db_session.commit()
    
    visit_data = {
        "card_id": card.card_id,
        "doctor_id": 1,
        "complaints": "Fever and cough"
    }
    
    response = client.post(
        "/visits",
        json=visit_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["complaints"] == "Fever and cough"
    assert data["status"] == "in_progress"

def test_complete_visit(auth_headers, db_session):
    """Тест завершения визита (Sequence Diagram)"""
    # Создаем визит
    from server.models import Patient, MedicalCard, Visit
    from datetime import date
    
    patient = Patient(
        full_name="Complete Visit Patient",
        passport_data="3333 333333",
        birth_date=date(1985, 7, 20)
    )
    db_session.add(patient)
    db_session.commit()
    
    card = MedicalCard(
        patient_id=patient.patient_id,
        registrar_id=1
    )
    db_session.add(card)
    db_session.commit()
    
    visit = Visit(
        card_id=card.card_id,
        doctor_id=1,
        status="in_progress"
    )
    db_session.add(visit)
    db_session.commit()
    
    # Завершаем визит
    response = client.put(
        f"/visits/{visit.visit_id}/complete",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    
    # Проверяем статус
    visit = db_session.query(Visit).filter(Visit.visit_id == visit.visit_id).first()
    assert visit.status == "completed"

def test_create_diagnosis(auth_headers, db_session):
    """Тест создания диагноза (Sequence Diagram)"""
    # Создаем визит
    from server.models import Patient, MedicalCard, Visit
    from datetime import date
    
    patient = Patient(
        full_name="Diagnosis Test Patient",
        passport_data="2222 222222",
        birth_date=date(1982, 4, 10)
    )
    db_session.add(patient)
    db_session.commit()
    
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
    
    diagnosis_data = {
        "visit_id": visit.visit_id,
        "severity": "severe",
        "description": "Pneumonia"
    }
    
    response = client.post(
        "/diagnoses",
        json=diagnosis_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Pneumonia"

def test_unauthorized_access():
    """Тест доступа без авторизации"""
    response = client.get("/patients")
    assert response.status_code == 401

def test_validation_error(auth_headers):
    """Тест валидации данных"""
    invalid_patient = {
        "full_name": "",  # Пустое имя
        "passport_data": "123",  # Слишком короткий
    }
    
    response = client.post(
        "/patients",
        json=invalid_patient,
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation Error
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Staff(Base):
    """Модель персонала (Врачи и Регистраторы)"""
    __tablename__ = "staff"
    
    staff_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)  # 'doctor' или 'registrar'
    specialization = Column(String(100), nullable=True)
    login_mis = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Relationships
    medical_cards = relationship("MedicalCard", back_populates="registrar")
    visits_as_doctor = relationship("Visit", back_populates="doctor", foreign_keys="Visit.doctor_id")

class Patient(Base):
    """Модель пациента"""
    __tablename__ = "patients"
    
    patient_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    passport_data = Column(String(20), unique=True, nullable=False)
    birth_date = Column(Date, nullable=False)
    address = Column(String(200))
    phone = Column(String(20))
    
    # Relationships
    medical_cards = relationship("MedicalCard", back_populates="patient", cascade="all, delete-orphan")

class MedicalCard(Base):
    """Медицинская карта пациента"""
    __tablename__ = "medical_cards"
    
    card_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    registrar_id = Column(Integer, ForeignKey("staff.staff_id"), nullable=False)
    created_date = Column(Date, default=datetime.now().date)
    status = Column(String(20), default="active")
    
    # Relationships
    patient = relationship("Patient", back_populates="medical_cards")
    registrar = relationship("Staff", back_populates="medical_cards")
    visits = relationship("Visit", back_populates="card", cascade="all, delete-orphan")

class Visit(Base):
    """Визит/Прием пациента"""
    __tablename__ = "visits"
    
    visit_id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("medical_cards.card_id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("staff.staff_id"), nullable=False)
    complaints = Column(Text)
    visit_date = Column(DateTime, default=datetime.now)
    status = Column(String(20), default="in_progress")  # in_progress, completed, cancelled
    
    # Relationships
    card = relationship("MedicalCard", back_populates="visits")
    doctor = relationship("Staff", back_populates="visits_as_doctor", foreign_keys=[doctor_id])
    diagnoses = relationship("Diagnosis", back_populates="visit", cascade="all, delete-orphan")
    treatment_plan = relationship("TreatmentPlan", back_populates="visit", uselist=False, cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="visit", cascade="all, delete-orphan")

class Diagnosis(Base):
    """Диагноз"""
    __tablename__ = "diagnoses"
    
    diagnosis_id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.visit_id"), nullable=False)
    severity = Column(String(50))  # mild, moderate, severe
    description = Column(Text, nullable=False)
    
    # Relationship
    visit = relationship("Visit", back_populates="diagnoses")

class TreatmentPlan(Base):
    """План лечения"""
    __tablename__ = "treatment_plans"
    
    plan_id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.visit_id"), unique=True, nullable=False)
    service_id = Column(Integer, ForeignKey("services.service_id"))
    doctor_conclusion = Column(Text)
    
    # Relationships
    visit = relationship("Visit", back_populates="treatment_plan")
    service = relationship("Service")

class Service(Base):
    """Медицинская услуга"""
    __tablename__ = "services"
    
    service_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    cost = Column(Numeric(10, 2), nullable=False)
    type = Column(String(50))
    
    # Relationship
    treatment_plans = relationship("TreatmentPlan", back_populates="service")

class Equipment(Base):
    """Медицинское оборудование"""
    __tablename__ = "equipment"
    
    equipment_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    inventory_number = Column(String(50), unique=True)
    status = Column(String(20), default="available")  # available, in_use, maintenance

class Payment(Base):
    """Оплата услуг"""
    __tablename__ = "payments"
    
    payment_id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.visit_id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_type = Column(String(50))  # cash, card, insurance
    document_number = Column(String(50))
    payment_date = Column(DateTime, default=datetime.now)
    
    # Relationship
    visit = relationship("Visit", back_populates="payments")
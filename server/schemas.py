from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


class StaffBase(BaseModel):
    full_name: str
    role: str
    login_mis: str
    specialization: Optional[str] = None

class StaffCreate(StaffBase):
    password: str

class StaffUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    specialization: Optional[str] = None

class StaffResponse(StaffBase):
    staff_id: int
    
    class Config:
        from_attributes = True

class PatientBase(BaseModel):
    full_name: str
    passport_data: str
    birth_date: date
    address: Optional[str] = None
    phone: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    passport_data: Optional[str] = None
    birth_date: Optional[date] = None
    address: Optional[str] = None
    phone: Optional[str] = None

class PatientResponse(PatientBase):
    patient_id: int
    
    class Config:
        from_attributes = True


class MedicalCardBase(BaseModel):
    patient_id: int
    registrar_id: int
    status: Optional[str] = "active"

class MedicalCardCreate(MedicalCardBase):
    pass

class MedicalCardResponse(BaseModel):
    card_id: int
    patient_id: int
    registrar_id: int
    created_date: date
    status: str
    
    class Config:
        from_attributes = True

class VisitBase(BaseModel):
    card_id: int
    doctor_id: int
    complaints: Optional[str] = None
    status: Optional[str] = "in_progress"

class VisitCreate(VisitBase):
    pass

class VisitUpdate(BaseModel):
    complaints: Optional[str] = None
    status: Optional[str] = None

class VisitResponse(BaseModel):
    visit_id: int
    card_id: int
    doctor_id: int
    complaints: Optional[str]
    visit_date: datetime
    status: str
    
    class Config:
        from_attributes = True

class DiagnosisBase(BaseModel):
    visit_id: int
    severity: Optional[str] = None
    description: str

class DiagnosisCreate(DiagnosisBase):
    pass

class DiagnosisResponse(BaseModel):
    diagnosis_id: int
    visit_id: int
    severity: Optional[str]
    description: str
    
    class Config:
        from_attributes = True

class TreatmentPlanBase(BaseModel):
    visit_id: int
    service_id: Optional[int] = None
    doctor_conclusion: Optional[str] = None

class TreatmentPlanCreate(TreatmentPlanBase):
    pass

class TreatmentPlanResponse(BaseModel):
    plan_id: int
    visit_id: int
    service_id: Optional[int]
    doctor_conclusion: Optional[str]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    login: str
    password: str

class PaymentBase(BaseModel):
    visit_id: int
    payment_type: str
    amount: float

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    payment_type: Optional[str] = None
    amount: Optional[float] = None

class PaymentResponse(PaymentBase):
    payment_id: int
    payment_date: datetime
    
    class Config:
        from_attributes = True
        
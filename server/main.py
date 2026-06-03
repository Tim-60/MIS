from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta

from .database import get_db, init_db
from .models import Staff, Patient, Visit, Diagnosis, TreatmentPlan
from .auth import (
    authenticate_user, 
    create_access_token, 
    get_current_user,
    settings
)
from .repositories import (
    StaffRepository, 
    PatientRepository, 
    VisitRepository,
    DiagnosisRepository,
    TreatmentPlanRepository,
    RepositoryFactory
)
from .schemas import (
    StaffCreate, StaffResponse, StaffUpdate,
    PatientCreate, PatientResponse, PatientUpdate,
    VisitCreate, VisitResponse, VisitUpdate,
    DiagnosisCreate, DiagnosisResponse,
    TreatmentPlanCreate, TreatmentPlanResponse,
    Token, UserLogin
)

app = FastAPI(
    title="Medical Information System",
    description="MIS API with Repository Pattern",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    init_db()


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Получение токена доступа"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login_mis, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, credentials.login, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password"
        )
    
    access_token = create_access_token(
        data={"sub": user.login_mis, "role": user.role}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}



@app.post("/staff", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
async def create_staff(
    staff: StaffCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    repo = StaffRepository(db)
    
    existing = repo.find({"login_mis": staff.login_mis})
    if existing:
        raise HTTPException(status_code=400, detail="Login already exists")
    
    db_staff = Staff(**staff.dict())
    return repo.add(db_staff)

@app.get("/staff", response_model=List[StaffResponse])
async def get_all_staff(
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получение всех сотрудников"""
    repo = StaffRepository(db)
    return repo.get_all()

@app.get("/staff/{staff_id}", response_model=StaffResponse)
async def get_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получение сотрудника по ID"""
    repo = StaffRepository(db)
    staff = repo.get_by_id(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff

@app.put("/staff/{staff_id}", response_model=StaffResponse)
async def update_staff(
    staff_id: int,
    staff_update: StaffUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Обновление информации о сотруднике"""
    repo = StaffRepository(db)
    existing_staff = repo.get_by_id(staff_id)
    if not existing_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    update_data = staff_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_staff, field, value)
    
    return repo.update(existing_staff)

@app.delete("/staff/{staff_id}")
async def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Удаление сотрудника"""
    repo = StaffRepository(db)
    if not repo.delete(staff_id):
        raise HTTPException(status_code=404, detail="Staff not found")
    return {"message": "Staff deleted successfully"}



@app.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Регистрация нового пациента"""
    repo = PatientRepository(db)
    
    # Проверка уникальности паспортных данных
    existing = repo.find({"passport_data": patient.passport_data})
    if existing:
        raise HTTPException(status_code=400, detail="Patient with this passport already exists")
    
    db_patient = Patient(**patient.dict())
    return repo.add(db_patient)

@app.get("/patients", response_model=List[PatientResponse])
async def get_all_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получение списка пациентов с пагинацией"""
    repo = PatientRepository(db)
    patients = repo.get_all()
    return patients[skip:skip + limit]

@app.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получение пациента по ID"""
    repo = PatientRepository(db)
    patient = repo.get_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.put("/patients/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Обновление информации о пациенте"""
    repo = PatientRepository(db)
    existing_patient = repo.get_by_id(patient_id)
    if not existing_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    update_data = patient_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_patient, field, value)
    
    return repo.update(existing_patient)

@app.delete("/patients/{patient_id}")
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Удаление пациента"""
    repo = PatientRepository(db)
    if not repo.delete(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}

@app.get("/patients/search/name/{name}", response_model=List[PatientResponse])
async def search_patients_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Поиск пациентов по имени (SQL метод)"""
    repo = PatientRepository(db)
    results = repo.find_by_name_sql(name)
    return results



@app.post("/visits", response_model=VisitResponse, status_code=status.HTTP_201_CREATED)
async def create_visit(
    visit: VisitCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Создание нового визита (приема)"""
    repo = VisitRepository(db)
    db_visit = Visit(**visit.dict())
    return repo.add(db_visit)

@app.get("/visits", response_model=List[VisitResponse])
async def get_all_visits(
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получение всех визитов"""
    repo = VisitRepository(db)
    return repo.get_all()

@app.get("/visits/{visit_id}", response_model=VisitResponse)
async def get_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получение визита по ID"""
    repo = VisitRepository(db)
    visit = repo.get_by_id(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit

@app.put("/visits/{visit_id}", response_model=VisitResponse)
async def update_visit(
    visit_id: int,
    visit_update: VisitUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Обновление визита"""
    repo = VisitRepository(db)
    existing_visit = repo.get_by_id(visit_id)
    if not existing_visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    
    update_data = visit_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_visit, field, value)
    
    return repo.update(existing_visit)

@app.put("/visits/{visit_id}/complete")
async def complete_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Завершение визита (Sequence Diagram step 31)"""
    repo = VisitRepository(db)
    success = repo.update_status_sql(visit_id, "completed")
    if not success:
        raise HTTPException(status_code=404, detail="Visit not found")
    return {"message": "Visit completed successfully"}

@app.get("/visits/doctor/{doctor_id}", response_model=List[VisitResponse])
async def get_visits_by_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получение визитов конкретного врача"""
    repo = VisitRepository(db)
    return repo.find_by_doctor(doctor_id)



@app.post("/diagnoses", response_model=DiagnosisResponse, status_code=status.HTTP_201_CREATED)
async def create_diagnosis(
    diagnosis: DiagnosisCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Добавление диагноза (Sequence Diagram step 16-18)"""
    repo = DiagnosisRepository(db)
    db_diagnosis = Diagnosis(**diagnosis.dict())
    return repo.add(db_diagnosis)

@app.get("/diagnoses/visit/{visit_id}", response_model=List[DiagnosisResponse])
async def get_diagnoses_by_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получение диагнозов по визиту"""
    repo = DiagnosisRepository(db)
    return repo.find({"visit_id": visit_id})


@app.post("/treatment_plans", response_model=TreatmentPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_treatment_plan(
    treatment_plan: TreatmentPlanCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Назначение плана лечения (Sequence Diagram step 23-25)"""
    repo = TreatmentPlanRepository(db)
    db_plan = TreatmentPlan(**treatment_plan.dict())
    return repo.add(db_plan)

@app.get("/treatment_plans/visit/{visit_id}", response_model=TreatmentPlanResponse)
async def get_treatment_plan_by_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получение плана лечения по визиту"""
    repo = TreatmentPlanRepository(db)
    plans = repo.find({"visit_id": visit_id})
    if not plans:
        raise HTTPException(status_code=404, detail="Treatment plan not found")
    return plans[0]



@app.get("/")
async def root():
    return {"message": "Medical Information System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
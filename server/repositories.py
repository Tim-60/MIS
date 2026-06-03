from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from .models import Staff, Patient, MedicalCard, Visit, Diagnosis, TreatmentPlan, Service, Payment
from .auth import get_password_hash

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    """Базовый интерфейс репозитория (Repository Pattern)"""
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        pass
    
    @abstractmethod
    def add(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        pass
    
    @abstractmethod
    def find(self, filters: Dict[str, Any]) -> List[T]:
        pass

class StaffRepository(IRepository[Staff]):
    """Репозиторий для работы с персоналом"""
    
    def __init__(self, session: Session):
        self.session = session
        self.model = Staff
    
    # ORM методы
    def get_by_id(self, id: int) -> Optional[Staff]:
        return self.session.query(Staff).filter(Staff.staff_id == id).first()
    
    def get_all(self) -> List[Staff]:
        return self.session.query(Staff).all()
    
    def add(self, entity: Staff) -> Staff:
        # Хешируем пароль перед сохранением
        if entity.password_hash and not entity.password_hash.startswith('$'):
            entity.password_hash = get_password_hash(entity.password_hash)
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity
    
    def update(self, entity: Staff) -> Staff:
        db_entity = self.get_by_id(entity.staff_id)
        if db_entity:
            for field, value in entity.__dict__.items():
                if not field.startswith('_') and value is not None:
                    setattr(db_entity, field, value)
            self.session.commit()
            self.session.refresh(db_entity)
        return db_entity
    
    def delete(self, id: int) -> bool:
        entity = self.get_by_id(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False
    
    def find(self, filters: Dict[str, Any]) -> List[Staff]:
        query = self.session.query(Staff)
        for field, value in filters.items():
            if hasattr(Staff, field):
                query = query.filter(getattr(Staff, field) == value)
        return query.all()
    
    # Raw SQL методы
    def get_by_id_sql(self, id: int) -> Optional[Dict]:
        result = self.session.execute(
            text("SELECT * FROM staff WHERE staff_id = :id"),
            {"id": id}
        )
        row = result.fetchone()
        if row:
            return dict(row._mapping)
        return None
    
    def find_sql(self, filters: Dict[str, Any]) -> List[Dict]:
        query = "SELECT * FROM staff WHERE 1=1"
        params = {}
        for field, value in filters.items():
            query += f" AND {field} = :{field}"
            params[field] = value
        
        result = self.session.execute(text(query), params)
        return [dict(row._mapping) for row in result.fetchall()]
    
    def add_sql(self, full_name: str, role: str, login_mis: str, password: str, specialization: str = None) -> int:
        try:
            hashed_password = get_password_hash(password)
            result = self.session.execute(
                text("""
                    INSERT INTO staff (full_name, role, login_mis, password_hash, specialization)
                    VALUES (:full_name, :role, :login_mis, :password_hash, :specialization)
                    RETURNING staff_id
                """),
                {
                    "full_name": full_name,
                    "role": role,
                    "login_mis": login_mis,
                    "password_hash": hashed_password,
                    "specialization": specialization
                }
            )
            self.session.commit()
            return result.fetchone()[0]
        except Exception:
            self.session.rollback()
            raise

class PatientRepository(IRepository[Patient]):
    """Репозиторий для работы с пациентами"""
    
    def __init__(self, session: Session):
        self.session = session
        self.model = Patient
    
    def get_by_id(self, id: int) -> Optional[Patient]:
        return self.session.query(Patient).filter(Patient.patient_id == id).first()
    
    def get_all(self) -> List[Patient]:
        return self.session.query(Patient).all()
    
    def add(self, entity: Patient) -> Patient:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity
    
    def update(self, entity: Patient) -> Patient:
        db_entity = self.get_by_id(entity.patient_id)
        if db_entity:
            for field, value in entity.__dict__.items():
                if not field.startswith('_') and value is not None:
                    setattr(db_entity, field, value)
            self.session.commit()
            self.session.refresh(db_entity)
        return db_entity
    
    def delete(self, id: int) -> bool:
        entity = self.get_by_id(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False
    
    def find(self, filters: Dict[str, Any]) -> List[Patient]:
        query = self.session.query(Patient)
        for field, value in filters.items():
            if hasattr(Patient, field):
                query = query.filter(getattr(Patient, field) == value)
        return query.all()
    
    # Raw SQL методы
    def find_by_name_sql(self, name: str) -> List[Dict]:
        result = self.session.execute(
            text("SELECT * FROM patients WHERE full_name LIKE :name"),
            {"name": f"%{name}%"}
        )
        return [dict(row._mapping) for row in result.fetchall()]
    
    def find_by_date_range_sql(self, start_date: str, end_date: str) -> List[Dict]:
        result = self.session.execute(
            text("""
                SELECT * FROM patients 
                WHERE birth_date BETWEEN :start AND :end
            """),
            {"start": start_date, "end": end_date}
        )
        return [dict(row._mapping) for row in result.fetchall()]

class VisitRepository(IRepository[Visit]):
    """Репозиторий для работы с визитами"""
    
    def __init__(self, session: Session):
        self.session = session
        self.model = Visit
    
    def get_by_id(self, id: int) -> Optional[Visit]:
        return self.session.query(Visit).filter(Visit.visit_id == id).first()
    
    def get_all(self) -> List[Visit]:
        return self.session.query(Visit).all()
    
    def add(self, entity: Visit) -> Visit:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity
    
    def update(self, entity: Visit) -> Visit:
        db_entity = self.get_by_id(entity.visit_id)
        if db_entity:
            for field, value in entity.__dict__.items():
                if not field.startswith('_') and value is not None:
                    setattr(db_entity, field, value)
            self.session.commit()
            self.session.refresh(db_entity)
        return db_entity
    
    def delete(self, id: int) -> bool:
        entity = self.get_by_id(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False
    
    def find(self, filters: Dict[str, Any]) -> List[Visit]:
        query = self.session.query(Visit)
        for field, value in filters.items():
            if hasattr(Visit, field):
                query = query.filter(getattr(Visit, field) == value)
        return query.all()
    
    # Специфичные методы
    def find_by_doctor(self, doctor_id: int) -> List[Visit]:
        return self.session.query(Visit).filter(Visit.doctor_id == doctor_id).all()
    
    def find_by_date_range(self, start: str, end: str) -> List[Visit]:
        return self.session.query(Visit).filter(
            Visit.visit_date.between(start, end)
        ).all()
    
    # Raw SQL методы
    def find_by_doctor_sql(self, doctor_id: int) -> List[Dict]:
        result = self.session.execute(
            text("SELECT * FROM visits WHERE doctor_id = :doctor_id"),
            {"doctor_id": doctor_id}
        )
        return [dict(row._mapping) for row in result.fetchall()]
    
    def update_status_sql(self, visit_id: int, status: str) -> bool:
        """Обновление статуса визита через raw SQL с обработкой транзакции"""
        try:
            result = self.session.execute(
                text("UPDATE visits SET status = :status WHERE visit_id = :id"),
                {"status": status, "id": visit_id}
            )
            self.session.commit()
            return result.rowcount > 0
        except Exception:
            self.session.rollback()
            return False

class DiagnosisRepository(IRepository[Diagnosis]):
    """Репозиторий для работы с диагнозами"""
    
    def __init__(self, session: Session):
        self.session = session
        self.model = Diagnosis
    
    def get_by_id(self, id: int) -> Optional[Diagnosis]:
        return self.session.query(Diagnosis).filter(Diagnosis.diagnosis_id == id).first()
    
    def get_all(self) -> List[Diagnosis]:
        return self.session.query(Diagnosis).all()
    
    def add(self, entity: Diagnosis) -> Diagnosis:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity
    
    def update(self, entity: Diagnosis) -> Diagnosis:
        db_entity = self.get_by_id(entity.diagnosis_id)
        if db_entity:
            for field, value in entity.__dict__.items():
                if not field.startswith('_') and value is not None:
                    setattr(db_entity, field, value)
            self.session.commit()
            self.session.refresh(db_entity)
        return db_entity
    
    def delete(self, id: int) -> bool:
        entity = self.get_by_id(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False
    
    def find(self, filters: Dict[str, Any]) -> List[Diagnosis]:
        query = self.session.query(Diagnosis)
        for field, value in filters.items():
            if hasattr(Diagnosis, field):
                query = query.filter(getattr(Diagnosis, field) == value)
        return query.all()

class TreatmentPlanRepository(IRepository[TreatmentPlan]):
    """Репозиторий для работы с планами лечения"""
    
    def __init__(self, session: Session):
        self.session = session
        self.model = TreatmentPlan
    
    def get_by_id(self, id: int) -> Optional[TreatmentPlan]:
        return self.session.query(TreatmentPlan).filter(TreatmentPlan.plan_id == id).first()
    
    def get_all(self) -> List[TreatmentPlan]:
        return self.session.query(TreatmentPlan).all()
    
    def add(self, entity: TreatmentPlan) -> TreatmentPlan:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity
    
    def update(self, entity: TreatmentPlan) -> TreatmentPlan:
        db_entity = self.get_by_id(entity.plan_id)
        if db_entity:
            for field, value in entity.__dict__.items():
                if not field.startswith('_') and value is not None:
                    setattr(db_entity, field, value)
            self.session.commit()
            self.session.refresh(db_entity)
        return db_entity
    
    def delete(self, id: int) -> bool:
        entity = self.get_by_id(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False
    
    def find(self, filters: Dict[str, Any]) -> List[TreatmentPlan]:
        query = self.session.query(TreatmentPlan)
        for field, value in filters.items():
            if hasattr(TreatmentPlan, field):
                query = query.filter(getattr(TreatmentPlan, field) == value)
        return query.all()

# Factory для создания репозиториев
class RepositoryFactory:
    """Factory Method Pattern для создания репозиториев"""
    
    @staticmethod
    def get_repository(repo_type: str, session: Session):
        repositories = {
            'staff': StaffRepository,
            'patient': PatientRepository,
            'visit': VisitRepository,
            'diagnosis': DiagnosisRepository,
            'treatment_plan': TreatmentPlanRepository
        }
        
        if repo_type not in repositories:
            raise ValueError(f"Unknown repository type: {repo_type}")
        
        return repositories[repo_type](session)
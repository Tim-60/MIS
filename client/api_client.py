import requests
from typing import Optional, List, Dict, Any
from datetime import datetime

class APIClient:
    """HTTP клиент для взаимодействия с сервером"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.headers = {}
    
    def _get_headers(self) -> Dict[str, str]:
        """Получение заголовков с токеном авторизации"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    
    def login(self, login: str, password: str) -> bool:
        """Авторизация пользователя"""
        try:
            response = requests.post(
                f"{self.base_url}/login",
                json={"login": login, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                return True
            return False
        except requests.RequestException:
            return False
    
    def logout(self):
        """Выход из системы"""
        self.token = None
    
    
    def get_patients(self) -> List[Dict]:
        """Получение списка всех пациентов"""
        response = requests.get(
            f"{self.base_url}/patients",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_patient(self, patient_id: int) -> Dict:
        """Получение пациента по ID"""
        response = requests.get(
            f"{self.base_url}/patients/{patient_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def create_patient(self, patient_data: Dict) -> Dict:
        """Создание нового пациента"""
        response = requests.post(
            f"{self.base_url}/patients",
            json=patient_data,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def update_patient(self, patient_id: int, patient_data: Dict) -> Dict:
        """Обновление пациента"""
        response = requests.put(
            f"{self.base_url}/patients/{patient_id}",
            json=patient_data,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def delete_patient(self, patient_id: int) -> bool:
        """Удаление пациента"""
        response = requests.delete(
            f"{self.base_url}/patients/{patient_id}",
            headers=self._get_headers()
        )
        return response.status_code == 200
    
    def search_patients(self, name: str) -> List[Dict]:
        """Поиск пациентов по имени"""
        response = requests.get(
            f"{self.base_url}/patients/search/name/{name}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    
    def create_visit(self, card_id: int, doctor_id: int, complaints: str) -> Dict:
        """Создание нового визита"""
        response = requests.post(
            f"{self.base_url}/visits",
            json={
                "card_id": card_id,
                "doctor_id": doctor_id,
                "complaints": complaints,
                "status": "in_progress"
            },
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def complete_visit(self, visit_id: int) -> bool:
        """Завершение визита"""
        response = requests.put(
            f"{self.base_url}/visits/{visit_id}/complete",
            headers=self._get_headers()
        )
        return response.status_code == 200
    
    def get_visits_by_doctor(self, doctor_id: int) -> List[Dict]:
        """Получение визитов врача"""
        response = requests.get(
            f"{self.base_url}/visits/doctor/{doctor_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    
    def create_diagnosis(self, visit_id: int, severity: str, description: str) -> Dict:
        response = requests.post(
            f"{self.base_url}/diagnoses",
            json={
                "visit_id": visit_id,
                "severity": severity,
                "description": description
            },
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    
    def create_treatment_plan(self, visit_id: int, doctor_conclusion: str) -> Dict:
        response = requests.post(
            f"{self.base_url}/treatment_plans",
            json={
                "visit_id": visit_id,
                "doctor_conclusion": doctor_conclusion
            },
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
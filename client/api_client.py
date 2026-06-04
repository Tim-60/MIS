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
    
    
    
    def create_payment(self, visit_id: int, payment_type: str, amount: float) -> Dict:
        """
        Создание записи об оплате приема
        
        Args:
            visit_id: ID визита
            payment_type: Тип оплаты ("insurance" для страховки, "out_of_pocket" для собственного счета)
            amount: Сумма оплаты
        
        Returns:
            Dict: Данные созданной записи оплаты
        """
        response = requests.post(
            f"{self.base_url}/payments",
            json={
                "visit_id": visit_id,
                "payment_type": payment_type,
                "amount": amount
            },
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_payment_by_visit(self, visit_id: int) -> Optional[Dict]:
        """
        Получение информации об оплате визита
        
        Args:
            visit_id: ID визита
        
        Returns:
            Dict: Данные об оплате или None, если оплата не найдена
        """
        try:
            response = requests.get(
                f"{self.base_url}/payments/visit/{visit_id}",
                headers=self._get_headers()
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
    
    def update_payment(self, payment_id: int, payment_data: Dict) -> Dict:
        """
        Обновление записи об оплате
        
        Args:
            payment_id: ID записи оплаты
            payment_data: Данные для обновления
        
        Returns:
            Dict: Обновленные данные оплаты
        """
        response = requests.put(
            f"{self.base_url}/payments/{payment_id}",
            json=payment_data,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def delete_payment(self, payment_id: int) -> bool:
        """
        Удаление записи об оплате
        
        Args:
            payment_id: ID записи оплаты
        
        Returns:
            bool: True если успешно удалено
        """
        response = requests.delete(
            f"{self.base_url}/payments/{payment_id}",
            headers=self._get_headers()
        )
        return response.status_code == 200
    
    def get_payments_history(self, patient_id: Optional[int] = None) -> List[Dict]:
        """
        Получение истории оплат (опционально по пациенту)
        
        Args:
            patient_id: ID пациента (если None, возвращает все оплаты)
        
        Returns:
            List[Dict]: Список записей об оплате
        """
        if patient_id:
            endpoint = f"{self.base_url}/payments/patient/{patient_id}"
        else:
            endpoint = f"{self.base_url}/payments"
        
        response = requests.get(
            endpoint,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_visits_full_info(self, doctor_id: int) -> List[Dict]:
        """Получение визитов с полной информацией (пациент, диагноз, оплата)"""
        response = requests.get(
            f"{self.base_url}/visits/doctor/{doctor_id}/full",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
import cmd
import json
from typing import Optional
from .api_client import APIClient

class MedicalConsole(cmd.Cmd):
    """Консольный клиент для МИС"""
    
    intro = "Добро пожаловать в Медицинскую Информационную Систему (CLI)"
    prompt = "(mis) "
    
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.current_user: Optional[str] = None
    
    def do_login(self, args):
        """Авторизация: login <username> <password>"""
        parts = args.split()
        if len(parts) != 2:
            print("Использование: login <username> <password>")
            return
        
        username, password = parts
        if self.api_client.login(username, password):
            self.current_user = username
            print(f"Успешный вход как {username}")
        else:
            print("Ошибка авторизации")
    
    def do_patients(self, args):
        """Показать всех пациентов: patients"""
        if not self.api_client.token:
            print("Требуется авторизация")
            return
        
        try:
            patients = self.api_client.get_patients()
            print(json.dumps(patients, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def do_search(self, args):
        """Поиск пациента по имени: search <name>"""
        if not args:
            print("Использование: search <name>")
            return
        
        try:
            patients = self.api_client.search_patients(args)
            print(json.dumps(patients, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def do_visit(self, args):
        """Создать визит: visit <card_id> <doctor_id> <complaints>"""
        parts = args.split(maxsplit=2)
        if len(parts) != 3:
            print("Использование: visit <card_id> <doctor_id> <complaints>")
            return
        
        try:
            card_id = int(parts[0])
            doctor_id = int(parts[1])
            complaints = parts[2]
            
            result = self.api_client.create_visit(card_id, doctor_id, complaints)
            print(f"Визит создан: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def do_diagnosis(self, args):
        """Добавить диагноз: diagnosis <visit_id> <severity> <description>"""
        parts = args.split(maxsplit=2)
        if len(parts) != 3:
            print("Использование: diagnosis <visit_id> <severity> <description>")
            return
        
        try:
            visit_id = int(parts[0])
            severity = parts[1]
            description = parts[2]
            
            result = self.api_client.create_diagnosis(visit_id, severity, description)
            print(f"Диагноз добавлен: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def do_complete(self, args):
        """Завершить визит: complete <visit_id>"""
        if not args:
            print("Использование: complete <visit_id>")
            return
        
        try:
            visit_id = int(args)
            if self.api_client.complete_visit(visit_id):
                print(f"Визит {visit_id} завершен")
            else:
                print("Ошибка завершения визита")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def do_logout(self, args):
        """Выйти из системы"""
        self.api_client.logout()
        self.current_user = None
        print("Вы вышли из системы")
    
    def do_exit(self, args):
        """Выйти из приложения"""
        print("До свидания!")
        return True
    
    def do_EOF(self, args):
        """Обработка Ctrl+D"""
        print()
        return self.do_exit(args)

def main():
    """Запуск консольного клиента"""
    MedicalConsole().cmdloop()

if __name__ == "__main__":
    main()
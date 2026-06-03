import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict
from datetime import datetime
from .api_client import APIClient

class LoginWindow:
    
    def __init__(self, root, api_client: APIClient):
        self.root = root
        self.api_client = api_client
        self.root.title("Вход в систему")
        self.root.geometry("300x200")
        
        self._create_widgets()
    
    def _create_widgets(self):
        tk.Label(self.root, text="Медицинская Информационная Система").pack(pady=10)
        
        tk.Label(self.root, text="Логин:").pack()
        self.login_entry = tk.Entry(self.root)
        self.login_entry.pack(pady=5)
        
        tk.Label(self.root, text="Пароль:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)
        
        tk.Button(
            self.root, 
            text="Войти", 
            command=self._login,
            bg="#4CAF50",
            fg="white"
        ).pack(pady=20)
    
    def _login(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        
        if self.api_client.login(login, password):
            self.root.destroy()
            return True
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
            return False

class MedicalApp:
    """Основное приложение (АРМ Врача/Регистратора)"""
    
    def __init__(self, root, api_client: APIClient):
        self.root = root
        self.api_client = api_client
        self.root.title("Медицинская Информационная Система")
        self.root.geometry("1000x700")
        
        self.current_visit_id: Optional[int] = None
        self.current_patient_id: Optional[int] = None
        
        self._create_widgets()
        self._create_menu()
    
    def _create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.root)
        
        patient_menu = tk.Menu(menubar, tearoff=0)
        patient_menu.add_command(label="Поиск пациента", command=self._show_patient_search)
        patient_menu.add_command(label="Регистрация пациента", command=self._show_patient_registration)
        menubar.add_cascade(label="Пациенты", menu=patient_menu)
        
        visit_menu = tk.Menu(menubar, tearoff=0)
        visit_menu.add_command(label="Проведение приема", command=self._show_visit_form)
        visit_menu.add_command(label="История приемов", command=self._show_visit_history)
        menubar.add_cascade(label="Приемы", menu=visit_menu)
        
        self.root.config(menu=menubar)
    
    def _create_widgets(self):
        """Создание основных виджетов"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        
        self.search_frame = tk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Поиск пациента")
        self._create_search_tab()
        
    
        self.visit_frame = tk.Frame(self.notebook)
        self.notebook.add(self.visit_frame, text="Проведение приема")
        self._create_visit_tab()
        
       
        self.history_frame = tk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="История приемов")
        self._create_history_tab()
    
    def _create_search_tab(self):
        """Вкладка поиска пациентов"""
        search_panel = tk.Frame(self.search_frame)
        search_panel.pack(fill='x', padx=10, pady=10)
        
        tk.Label(search_panel, text="Поиск по имени:").pack(side='left')
        self.search_entry = tk.Entry(search_panel, width=40)
        self.search_entry.pack(side='left', padx=5)
        
        tk.Button(
            search_panel, 
            text="Найти", 
            command=self._search_patients
        ).pack(side='left', padx=5)
        
        tk.Button(
            search_panel, 
            text="Все пациенты", 
            command=self._load_all_patients
        ).pack(side='left', padx=5)
        
       
        columns = ('ID', 'ФИО', 'Дата рождения', 'Телефон', 'Паспорт')
        self.patient_tree = ttk.Treeview(self.search_frame, columns=columns, show='headings')
        
        for col in columns:
            self.patient_tree.heading(col, text=col)
            self.patient_tree.column(col, width=150)
        
        self.patient_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        
        btn_frame = tk.Frame(self.search_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(
            btn_frame, 
            text="Выбрать пациента", 
            command=self._select_patient
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame, 
            text="Редактировать", 
            command=self._edit_patient
        ).pack(side='left', padx=5)
    
    def _create_visit_tab(self):
        """Вкладка проведения приема"""
        
        patient_info = tk.LabelFrame(self.visit_frame, text="Информация о пациенте")
        patient_info.pack(fill='x', padx=10, pady=5)
        
        self.patient_info_label = tk.Label(patient_info, text="Пациент не выбран")
        self.patient_info_label.pack(pady=5)
        
        # Шаг 8-9: Создание визита
        visit_frame = tk.LabelFrame(self.visit_frame, text="Новый визит")
        visit_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(visit_frame, text="Жалобы:").pack(anchor='w')
        self.complaints_text = tk.Text(visit_frame, height=3, width=80)
        self.complaints_text.pack(pady=5)
        
        tk.Button(
            visit_frame, 
            text="Начать прием (Создать визит)", 
            command=self._start_visit,
            bg="#2196F3",
            fg="white"
        ).pack(pady=5)
        
        
        diagnosis_frame = tk.LabelFrame(self.visit_frame, text="Диагноз")
        diagnosis_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(diagnosis_frame, text="Тяжесть:").pack(anchor='w')
        self.severity_combo = ttk.Combobox(
            diagnosis_frame, 
            values=["Легкая", "Средняя", "Тяжелая"],
            state="readonly"
        )
        self.severity_combo.pack(fill='x', pady=5)
        self.severity_combo.set("Средняя")
        
        tk.Label(diagnosis_frame, text="Описание диагноза:").pack(anchor='w')
        self.diagnosis_text = tk.Text(diagnosis_frame, height=3, width=80)
        self.diagnosis_text.pack(pady=5)
        
        tk.Button(
            diagnosis_frame, 
            text="Сохранить диагноз", 
            command=self._save_diagnosis
        ).pack(pady=5)
        
        
        treatment_frame = tk.LabelFrame(self.visit_frame, text="План лечения")
        treatment_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(treatment_frame, text="Заключение врача:").pack(anchor='w')
        self.treatment_text = tk.Text(treatment_frame, height=3, width=80)
        self.treatment_text.pack(pady=5)
        
        tk.Button(
            treatment_frame, 
            text="Назначить план лечения", 
            command=self._save_treatment_plan
        ).pack(pady=5)
        
        
        tk.Button(
            self.visit_frame, 
            text="Завершить прием", 
            command=self._complete_visit,
            bg="#4CAF50",
            fg="white",
            font=('Arial', 12, 'bold')
        ).pack(pady=20)
    
    def _create_history_tab(self):
        """Вкладка истории приемов"""
        columns = ('ID', 'Дата', 'Пациент', 'Диагноз', 'Статус')
        self.history_tree = ttk.Treeview(self.history_frame, columns=columns, show='headings')
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)
        
        self.history_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Button(
            self.history_frame, 
            text="Обновить", 
            command=self._load_visit_history
        ).pack(pady=10)
    
    
    
    def _search_patients(self):
        """Поиск пациентов"""
        name = self.search_entry.get()
        if not name:
            messagebox.showwarning("Внимание", "Введите имя для поиска")
            return
        
        try:
            patients = self.api_client.search_patients(name)
            self._populate_patient_table(patients)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка поиска: {e}")
    
    def _load_all_patients(self):
        """Загрузка всех пациентов"""
        try:
            patients = self.api_client.get_patients()
            self._populate_patient_table(patients)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
    
    def _populate_patient_table(self, patients: List[Dict]):
        """Заполнение таблицы пациентов"""
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)
        
        for patient in patients:
            self.patient_tree.insert('', 'end', values=(
                patient['patient_id'],
                patient['full_name'],
                patient['birth_date'],
                patient.get('phone', ''),
                patient['passport_data']
            ))
    
    def _select_patient(self):
        """Выбор пациента для приема"""
        selected = self.patient_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите пациента")
            return
        
        item = self.patient_tree.item(selected[0])
        patient_id = item['values'][0]
        patient_name = item['values'][1]
        
        self.current_patient_id = patient_id
        self.patient_info_label.config(text=f"Пациент: {patient_name} (ID: {patient_id})")
        
        messagebox.showinfo("Успех", f"Выбран пациент: {patient_name}")
    
    def _edit_patient(self):
        """Редактирование пациента"""
        selected = self.patient_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите пациента")
            return
        
        
        messagebox.showinfo("Инфо", "Функция редактирования в разработке")
    
    def _show_patient_search(self):
        self.notebook.select(0)
    
    def _show_patient_registration(self):
        """Показ окна регистрации пациента"""
        self._open_patient_registration_window()
    
    
    
    def _start_visit(self):
        """Начало приема (Sequence Diagram steps 8-14)"""
        if not self.current_patient_id:
            messagebox.showwarning("Внимание", "Сначала выберите пациента")
            return
        
        complaints = self.complaints_text.get("1.0", tk.END).strip()
        if not complaints:
            messagebox.showwarning("Внимание", "Введите жалобы пациента")
            return
        
        try:
            
            visit_data = self.api_client.create_visit(
                card_id=1,  
                doctor_id=1,  
                complaints=complaints
            )
            
            self.current_visit_id = visit_data['visit_id']
            messagebox.showinfo("Успех", f"Визит создан! ID: {self.current_visit_id}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания визита: {e}")
    
    def _save_diagnosis(self):
        """Сохранение диагноза (Sequence Diagram steps 15-21)"""
        if not self.current_visit_id:
            messagebox.showwarning("Внимание", "Сначала начните прием")
            return
        
        severity_map = {"Легкая": "mild", "Средняя": "moderate", "Тяжелая": "severe"}
        severity = severity_map[self.severity_combo.get()]
        description = self.diagnosis_text.get("1.0", tk.END).strip()
        
        if not description:
            messagebox.showwarning("Внимание", "Введите описание диагноза")
            return
        
        try:
            
            self.api_client.create_diagnosis(
                visit_id=self.current_visit_id,
                severity=severity,
                description=description
            )
            messagebox.showinfo("Успех", "Диагноз сохранен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения диагноза: {e}")
    
    def _save_treatment_plan(self):
        """Сохранение плана лечения (Sequence Diagram steps 22-28)"""
        if not self.current_visit_id:
            messagebox.showwarning("Внимание", "Сначала начните прием")
            return
        
        conclusion = self.treatment_text.get("1.0", tk.END).strip()
        if not conclusion:
            messagebox.showwarning("Внимание", "Введите заключение врача")
            return
        
        try:
            
            self.api_client.create_treatment_plan(
                visit_id=self.current_visit_id,
                doctor_conclusion=conclusion
            )
            messagebox.showinfo("Успех", "План лечения назначен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения плана: {e}")
    
    def _complete_visit(self):
        """Завершение приема (Sequence Diagram steps 29-36)"""
        if not self.current_visit_id:
            messagebox.showwarning("Внимание", "Нет активного приема")
            return
        
        if messagebox.askyesno("Подтверждение", "Завершить прием?"):
            try:
                
                self.api_client.complete_visit(self.current_visit_id)
                
                messagebox.showinfo("Успех", "Прием завершен и сохранен!")
                
                
                self._clear_visit_form()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка завершения приема: {e}")
    
    def _clear_visit_form(self):
        """Очистка формы приема"""
        self.complaints_text.delete("1.0", tk.END)
        self.diagnosis_text.delete("1.0", tk.END)
        self.treatment_text.delete("1.0", tk.END)
        self.current_visit_id = None
    
    def _show_visit_form(self):
        self.notebook.select(1)
    
    def _show_visit_history(self):
        self.notebook.select(2)
        self._load_visit_history()
    
    def _load_visit_history(self):
        """Загрузка истории приемов"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        try:
            
            visits = self.api_client.get_visits_by_doctor(doctor_id=1)
            
            for visit in visits:
                self.history_tree.insert('', 'end', values=(
                    visit['visit_id'],
                    visit['visit_date'],
                    visit['card_id'],
                    "Диагноз",  
                    visit['status']
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки истории: {e}")
    
    def _open_patient_registration_window(self):
        """Окно регистрации нового пациента"""
        reg_window = tk.Toplevel(self.root)
        reg_window.title("Регистрация пациента")
        reg_window.geometry("400x400")
        
        tk.Label(reg_window, text="ФИО:").pack(pady=5)
        name_entry = tk.Entry(reg_window, width=40)
        name_entry.pack()
        
        tk.Label(reg_window, text="Паспортные данные:").pack(pady=5)
        passport_entry = tk.Entry(reg_window, width=40)
        passport_entry.pack()
        
        tk.Label(reg_window, text="Дата рождения (ГГГГ-ММ-ДД):").pack(pady=5)
        birth_entry = tk.Entry(reg_window, width=40)
        birth_entry.pack()
        
        tk.Label(reg_window, text="Телефон:").pack(pady=5)
        phone_entry = tk.Entry(reg_window, width=40)
        phone_entry.pack()
        
        tk.Label(reg_window, text="Адрес:").pack(pady=5)
        address_entry = tk.Entry(reg_window, width=40)
        address_entry.pack()
        
        def save_patient():
            try:
                patient_data = {
                    "full_name": name_entry.get(),
                    "passport_data": passport_entry.get(),
                    "birth_date": birth_entry.get(),
                    "phone": phone_entry.get(),
                    "address": address_entry.get()
                }
                
                self.api_client.create_patient(patient_data)
                messagebox.showinfo("Успех", "Пациент зарегистрирован")
                reg_window.destroy()
                self._load_all_patients()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка регистрации: {e}")
        
        tk.Button(
            reg_window, 
            text="Зарегистрировать", 
            command=save_patient,
            bg="#4CAF50",
            fg="white"
        ).pack(pady=20)

def main():
    """Точка входа в приложение"""
    api_client = APIClient()
    
    
    root = tk.Tk()
    login_window = LoginWindow(root, api_client)
    root.mainloop()
    
    
    if api_client.token:
        app_root = tk.Tk()
        app = MedicalApp(app_root, api_client)
        app_root.mainloop()

if __name__ == "__main__":
    main()
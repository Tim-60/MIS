import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from server.database import Base, get_db
from server.main import app
from server.models import Staff
from server.auth import get_password_hash

# Тестовая БД в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ❌ УДАЛИТЕ этот модульный override — он создаёт отдельную сессию
# app.dependency_overrides[get_db] = override_get_db  <-- удалить!

@pytest.fixture(scope="function")
def db_session():
    """Фикстура для сессии БД"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура тестового клиента с общей сессией"""
    # 🔥 Переопределяем get_db, чтобы возвращать ТОТУ ЖЕ сессию, что в тесте
    def override_get_db():
        yield db_session  # Одна сессия на тест + приложение
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    # Очищаем после теста, чтобы не влиял на другие
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Создание тестового пользователя"""
    user = Staff(
        full_name="Test Doctor",
        role="doctor",
        login_mis="test_doctor",
        password_hash=get_password_hash("test_password"),
        specialization="Therapy"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_token(client, test_user):
    """Получение токена авторизации"""
    response = client.post(
        "/token",
        data={"username": "test_doctor", "password": "test_password"}
    )
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(auth_token):
    """Заголовки с токеном"""
    return {"Authorization": f"Bearer {auth_token}"}
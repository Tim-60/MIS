import pytest
from server.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    authenticate_user
)
from server.models import Staff

def test_password_hashing():
    """Тест хеширования пароля"""
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)

def test_create_access_token():
    """Тест создания токена"""
    data = {"sub": "test_user", "role": "doctor"}
    token = create_access_token(data=data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

def test_authenticate_user(db_session, test_user):
    """Тест аутентификации пользователя"""
    # Успешная аутентификация
    user = authenticate_user(db_session, "test_doctor", "test_password")
    assert user is not None
    assert user.login_mis == "test_doctor"
    
    # Неверный пароль
    user = authenticate_user(db_session, "test_doctor", "wrong_password")
    assert user is False
    
    # Несуществующий пользователь
    user = authenticate_user(db_session, "nonexistent", "password")
    assert user is False

def test_login_endpoint(client, test_user):
    """Тест endpoint авторизации"""
    response = client.post(
        "/login",
        json={"login": "test_doctor", "password": "test_password"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    """Тест авторизации с неверным паролем"""
    response = client.post(
        "/login",
        json={"login": "test_doctor", "password": "wrong_password"}
    )
    
    assert response.status_code == 401

def test_protected_endpoint_without_token(client):
    """Тест защищенного endpoint без токена"""
    response = client.get("/staff")
    assert response.status_code == 401
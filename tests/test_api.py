from fastapi.testclient import TestClient
from models.llm import prediction_task
from unittest.mock import Mock
import pytest
import httpx
from sqlmodel import Session
from routes.llm import db_task, input_data
from database.config import get_settings
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from models.user import User, Admin
from services.crud.user import user as UserService
from routes.user import hash_password
from services.crud.llm import process_task_async

settings = get_settings()

def test_prediction_lifecycle(client: TestClient, mocker):
    mock_process = mocker.patch('services.crud.llm_inference.llm_service.process_request')
    mock_process.return_value = "test prediction"

    create_response = client.post(
        "/predict",
        json={"text": "test input"},
        headers={"Authorization": "Bearer test_token"}
    )
    assert create_response.status_code == 200
    task_data = create_response.json()
    task_id = task_data["task_id"]

    status_response = client.get(f"/status/{task_id}")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "pending"

    with Session() as session:
        process_task_async(
            task_id=task_id,
            input_data="test input",
            session=session
        )


    updated_status = client.get(f"/status/{task_id}")
    assert updated_status.json() == {
        "status": "completed",
        "result": "test prediction"
    }

    task_response = client.get(f"/api/events/{task_id}")
    assert task_response.json()["status"] == "completed"
    assert task_response.json()["result"] == "test prediction"

def test_create_prediction(client: TestClient):
    prediction_data = {
        "task_id": "test_task_id", 
        "input_data": "test input"  
    }
    
    response = client.post(
        "/api/events/new/",
        json=prediction_data,
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Prediction created successfully"}

def test_successful_signup(client: TestClient):
    response = client.post(
        "/user/signup",
        data={"email": "newuser@test.com", "password": "securepass123"}
    )
    assert response.status_code == 302
    assert "Bearer" in response.cookies.get(settings.COOKIE_NAME)

def test_signup_with_existing_email(client: TestClient):
    client.post("/user/signup", data={"email": "duplicate@test.com", "password": "pass"})
    response = client.post("/user/signup", data={"email": "duplicate@test.com", "password": "pass"})
    assert response.status_code == 409
    assert "already exists" in response.text

def test_successful_login(client: TestClient):
    client.post("/user/signup", data={"email": "login@test.com", "password": "pass"})
    response = client.post("/auth/login", data={"username": "login@test.com", "password": "pass"})
    assert response.status_code == 302
    assert "Bearer" in response.cookies.get(settings.COOKIE_NAME)


def test_successful_signin(client: TestClient):
    client.post(
        "/user/signup",
        data={"email": "login@test.com", "password": "pass"}
    )
    
    response = client.post(
        "/auth/login",
        data={"username": "login@test.com", "password": "pass"}
    )
    assert response.status_code == 302
    assert "Bearer" in response.cookies.get(settings.COOKIE_NAME)

def test_signin_invalid_password(client: TestClient):
    client.post(
        "/user/signup",
        data={"email": "user@test.com", "password": "pass"}
    )
    response = client.post(
        "/auth/login",
        data={"username": "user@test.com", "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_signin_nonexistent_user(client: TestClient):
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@test.com", "password": "pass"}
    )
    assert response.status_code == 404


def test_prediction_failure(client: TestClient, mocker):
    mocker.patch('services.crud.llm_inference.llm_service.process_request',
               side_effect=Exception("Test error"))

    create_response = client.post(
        "/predict",
        json={"text": "failing input"},
        headers={"Authorization": "Bearer test_token"} 
    )
    task_id = create_response.json()["task_id"]

    with Session() as session:
        process_task_async(
            task_id=task_id,
            input_data="failing input",
            session=session
        )

    status_response = client.get(f"/status/{task_id}")
    assert status_response.json() == {
        "status": "failed",
        "result": "Test error"
    }

def test_balance_on_prediction(client: TestClient, mocker):
    mocker.patch('services.crud.llm_inference.llm_service.process_request',
               return_value="balance test")

    initial_balance = client.get("/user/profile", 
    headers={"Authorization": "Bearer test_token"}).json()["balance"]

    client.post(
        "/predict",
        json={"text": "balance test"},
        headers={"Authorization": "Bearer test_token"}
    )

    updated_balance = client.get("/user/profile", 
    headers={"Authorization": "Bearer test_token"}).json()["balance"]
    assert updated_balance == initial_balance - 2

def test_balance_recharge(client: TestClient, session: Session):
    admin = Admin(email="admin@test.com", password=hash_password.create_hash("adminpass"))
    user = User(email="user@test.com", password="pass", balance=10)
    session.add_all([admin, user])
    session.commit()

    response = client.post(
        "/user/recharge",
        json={"user_id": user.user_id, "amount": 50, "admin_id": admin.admin_id},
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    assert response.json()["balance"] == 60


def test_balance_with_zero_balance(client: TestClient, session: Session):
    user = User(email="nobalance@test.com", password="pass", balance=0)
    session.add(user)
    session.commit()

    response = client.post(
        "/predict",
        json={"text": "test input"},
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 402
    assert "Insufficient balance" in response.text

def test_balance_recharge_unauthorized(client: TestClient):
    response = client.post(
        "/user/recharge",
        json={"user_id": 1, "amount": 50, "admin_id": 999}
    )
    assert response.status_code == 403

def test_negative_balance_recharge(client: TestClient, session: Session):
    admin = Admin(email="admin@test.com", password="pass")
    user = User(email="user@test.com", password="pass")
    session.add_all([admin, user])
    session.commit()
    
    response = client.post(
        "/user/recharge",
        json={"user_id": user.user_id, "amount": -100, "admin_id": admin.admin_id}
    )
    assert response.status_code == 400

def test_home_request(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    
def test_get_predictions(client: TestClient):
    response = client.get("/api/events/")
    assert response.status_code == 200
    assert response.json() == []
    
    
def test_get_prediction(client: TestClient):
   prediction_data = {"text": "test input"}
    
   response = client.post("/predict", json=prediction_data)
   assert response.status_code == 200
   assert "task_id" in response.json()
   assert response.json()["status"] == "pending"


def test_clear_predictions(client: TestClient):
    response = client.delete("/api/events/")
    
    assert response.status_code == 200
    assert response.json() == {"message": "predictions deleted successfully"}
    
def test_delete_prediction(client: TestClient):
    create_response = client.post(
        "/predict",
        json={"text": "test input"}
    )
    assert create_response.status_code == 200
    task_id = create_response.json()["task_id"]
    
    delete_response = client.delete(f"/api/events/{task_id}")
    assert delete_response.status_code == 200
    
    get_response = client.get(f"/api/events/{task_id}")
    assert get_response.status_code == 404


def test_transaction_history_after_prediction(client: TestClient):
    client.post("/predict", json={"text": "test input"})
    
    response = client.get("/user/history?user_id=1")
    history = response.json()["history"]
    
    assert len(history) > 0
    assert any(tx["description"].startswith("LLM request") for tx in history)


def test_prediction_with_insufficient_balance(client: TestClient, session: Session):
    
    user = session.get(User, 1)
    user.balance = 0
    session.commit()
    
    response = client.post("/predict", json={"text": "test input"})
    assert response.status_code == 402
    assert "Insufficient balance" in response.text

def test_access_protected_route_unauthorized(client: TestClient):
    response = client.get("/private")
    assert response.status_code == 403

def test_rabbitmq_integration(client: TestClient, mocker):
    mock_send = mocker.patch('services.rm.rm.send_task')
    
    response = client.post("/predict", json={"text": "integration test"})
    task_id = response.json()["task_id"]
    
    mock_send.assert_called_once_with({
        'task_id': task_id,
        'input_data': 'integration test',
        'llm_id': mocker.ANY
    })

def test_admin_access_control(client: TestClient, session: Session):
    regular_user = User(email="regular@test.com", password="pass")
    session.add(regular_user)
    session.commit()
    
    response = client.post(
        "/user/recharge",
        json={"user_id": 1, "amount": 50, "admin_id": regular_user.user_id}
    )
    assert response.status_code == 403

def test_invalid_email_signup(client: TestClient):
    response = client.post(
        "/user/signup",
        data={"email": "invalid-email", "password": "pass"}
    )
    assert response.status_code == 400
    assert "valid email" in response.text


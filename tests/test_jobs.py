import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.core.config import settings

from sqlalchemy.pool import StaticPool

# Test Database setup (using SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    from app.models import generation_job, certificate # ensure models are loaded
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_job():
    response = client.post(
        f"{settings.API_V1_STR}/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-08",
            "issuer_name": "ABC Institute",
            "recipients": [
                {"name": "Dinkar Arya", "email": "dinkar@example.com"},
                {"name": "Rahul Kumar", "email": "rahul@example.com"}
            ]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["event_name"] == "Python Workshop"
    assert data["total_count"] == 2
    assert "id" in data
    
def test_create_job_validation_error():
    response = client.post(
        f"{settings.API_V1_STR}/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-08",
            "issuer_name": "ABC Institute",
            "recipients": [] # empty recipients
        }
    )
    assert response.status_code == 422

def test_job_status_progress():
    # 1. Create Job
    response = client.post(
        f"{settings.API_V1_STR}/jobs",
        json={
            "event_name": "Go Workshop",
            "event_date": "2026-10-09",
            "issuer_name": "Tech Corp",
            "recipients": [{"name": "Alice"}]
        }
    )
    job_id = response.json()["id"]

    # 2. Check Status
    res = client.get(f"{settings.API_V1_STR}/jobs/{job_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["PENDING", "PROCESSING", "COMPLETED", "COMPLETED_WITH_ERRORS"]
    assert "progress_percentage" in data

def test_retrieving_certificates():
    # Get a 404 for a non-existent certificate
    res = client.get(f"{settings.API_V1_STR}/certificates/invalid_id")
    assert res.status_code == 404
    assert res.json()["detail"]["code"] == "CERTIFICATE_NOT_FOUND"

def test_certificate_generation_and_failure_handling(monkeypatch):
    # Mock the generator to simulate 1 success and 1 failure
    from app.services.certificate_generator import CertificateGenerator
    
    original_generate = CertificateGenerator.generate
    
    def mock_generate(self, job_id, certificate_id, recipient_name, event_name, event_date, issuer_name):
        if recipient_name == "FailMe":
            raise Exception("Simulated PDF generation failure")
        return f"/mock/path/{certificate_id}.pdf"
        
    monkeypatch.setattr(CertificateGenerator, "generate", mock_generate)
    
    # 1. Create a job with 1 valid and 1 failure-inducing recipient
    response = client.post(
        f"{settings.API_V1_STR}/jobs",
        json={
            "event_name": "Mock Event",
            "event_date": "2026-10-10",
            "issuer_name": "Mock Inc",
            "recipients": [{"name": "SuccessUser"}, {"name": "FailMe"}]
        }
    )
    job_id = response.json()["id"]
    
    # 2. To test the worker synchronously, we import and run it directly
    from app.workers.certificate_worker import process_generation_job
    process_generation_job(job_id)
    
    # 3. Check Job Status to ensure it is COMPLETED_WITH_ERRORS
    res = client.get(f"{settings.API_V1_STR}/jobs/{job_id}")
    data = res.json()
    
    assert data["status"] == "COMPLETED_WITH_ERRORS"
    assert data["total_count"] == 2
    assert data["success_count"] == 1
    assert data["failure_count"] == 1
    assert data["progress_percentage"] == 100

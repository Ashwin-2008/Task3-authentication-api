import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set testing environment before loading application
os.environ["APP_ENV"] = "testing"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-and-integration-tests-only-32chars"

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.admin import Admin
from app.models.submission import Submission, SubmissionStatus
from app.core.security import hash_password, create_access_token

# In-memory SQLite engine with StaticPool for thread-safe test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh isolated database for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_credentials():
    return {
        "username": "superadmin",
        "password": "StrongPassword123!",
    }


@pytest.fixture(scope="function")
def admin_user(db_session, admin_credentials):
    """Create an administrator in the test database."""
    hashed = hash_password(admin_credentials["password"])
    admin = Admin(
        username=admin_credentials["username"],
        password_hash=hashed,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def admin_token(admin_user):
    """Generate a valid JWT Bearer token for the test admin."""
    return create_access_token(data={"sub": admin_user.username, "admin_id": admin_user.id})


@pytest.fixture(scope="function")
def admin_auth_headers(admin_token):
    """Return authorization headers with Bearer token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="function")
def sample_submissions(db_session):
    """Create a curated set of sample submissions for testing."""
    submissions = [
        Submission(
            title="Smart Irrigation Network",
            description="IoT-based automated watering system for precision agriculture.",
            domain="Agriculture",
            github_url="https://github.com/codenova/smart-irrigation",
            demo_url="https://irrigation.example.com",
            status=SubmissionStatus.APPROVED.value,
            feedback="Great work, looks solid.",
        ),
        Submission(
            title="Crop Disease Classifier",
            description="Deep learning model to detect crop diseases from leaf images.",
            domain="Agriculture",
            github_url="https://github.com/codenova/crop-disease-ai",
            demo_url="https://cropdisease.example.com",
            status=SubmissionStatus.APPROVED.value,
        ),
        Submission(
            title="Microfinance Peer Lending",
            description="Decentralized microfinance credit platform for underserved communities.",
            domain="FinTech",
            github_url="https://github.com/codenova/microfinance-ledger",
            demo_url="https://fintech.example.com/app",
            status=SubmissionStatus.APPROVED.value,
        ),
        Submission(
            title="EHR Patient Portal",
            description="Encrypted electronic health record management for outpatient clinics.",
            domain="HealthCare",
            github_url="https://github.com/codenova/ehr-portal",
            demo_url="https://ehr.example.com",
            status=SubmissionStatus.PENDING.value,
        ),
        Submission(
            title="Faulty Crypto Exchange",
            description="A flawed implementation with security issues.",
            domain="FinTech",
            github_url="https://github.com/codenova/broken-exchange",
            demo_url="https://badcrypto.example.com",
            status=SubmissionStatus.REJECTED.value,
            feedback="Insecure API implementation and broken links.",
        ),
    ]

    for sub in submissions:
        db_session.add(sub)
    db_session.commit()
    return submissions


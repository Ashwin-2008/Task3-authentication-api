def test_health_check(client):
    """Health check endpoint should return 200 and status ok."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint(client):
    """Root endpoint should return application metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["health"] == "/api/v1/health"


def test_openapi_schema(client):
    """OpenAPI schema should be available and valid."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/submissions" in schema["paths"]
    assert "/api/v1/auth/login" in schema["paths"]


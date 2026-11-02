def test_create_valid_submission(client):
    """Submitting valid project data returns HTTP 201 and starts in Pending status."""
    payload = {
        "title": "Smart Agriculture Platform",
        "description": "A comprehensive sensor network platform for real-time crop health monitoring.",
        "domain": "Agriculture",
        "github_url": "https://github.com/example/agriculture-platform",
        "demo_url": "https://agriculture.example.com",
    }
    response = client.post("/api/v1/submissions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["domain"] == payload["domain"]
    assert data["github_url"] == payload["github_url"]
    assert data["demo_url"] == payload["demo_url"]
    assert data["status"] == "Pending"
    assert data["feedback"] is None
    assert data["reviewed_at"] is None
    assert "id" in data
    assert "created_at" in data


def test_reject_missing_title(client):
    """Request with missing title must return 422 validation error."""
    payload = {
        "description": "A comprehensive sensor network platform.",
        "domain": "Agriculture",
        "github_url": "https://github.com/example/agriculture-platform",
        "demo_url": "https://agriculture.example.com",
    }
    response = client.post("/api/v1/submissions", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_reject_empty_or_whitespace_title(client):
    """Empty or whitespace-only title must return 422 validation error."""
    payload = {
        "title": "   ",
        "description": "A comprehensive sensor network platform.",
        "domain": "Agriculture",
        "github_url": "https://github.com/example/agriculture-platform",
        "demo_url": "https://agriculture.example.com",
    }
    response = client.post("/api/v1/submissions", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_reject_short_description(client):
    """Short descriptions under 10 characters must be rejected."""
    payload = {
        "title": "Valid Title",
        "description": "Too short",
        "domain": "Agriculture",
        "github_url": "https://github.com/example/agriculture-platform",
        "demo_url": "https://agriculture.example.com",
    }
    response = client.post("/api/v1/submissions", json=payload)
    assert response.status_code == 422


def test_reject_invalid_github_url(client):
    """Invalid GitHub URL with bad scheme or malformed host must be rejected."""
    payload = {
        "title": "Valid Title",
        "description": "A valid description for testing project submission.",
        "domain": "AI/ML",
        "github_url": "http://github.com/example/insecure-repo",  # HTTP rejected
        "demo_url": "https://demo.example.com",
    }
    response = client.post("/api/v1/submissions", json=payload)
    assert response.status_code == 422


def test_reject_malicious_github_spoof(client):
    """Spoofed GitHub URL must be rejected."""
    payload = {
        "title": "Valid Title",
        "description": "A valid description for testing project submission.",
        "domain": "AI/ML",
        "github_url": "https://github.com.attacker.com/example/repo",
        "demo_url": "https://demo.example.com",
    }
    response = client.post("/api/v1/submissions", json=payload)
    assert response.status_code == 422


def test_reject_http_demo_url(client):
    """Demo URL using HTTP scheme must be rejected."""
    payload = {
        "title": "Valid Title",
        "description": "A valid description for testing project submission.",
        "domain": "AI/ML",
        "github_url": "https://github.com/example/valid-repo",
        "demo_url": "http://demo.example.com",  # HTTP rejected
    }
    response = client.post("/api/v1/submissions", json=payload)
    assert response.status_code == 422


def test_reject_malformed_json(client):
    """Malformed non-JSON request body should return 422 error."""
    response = client.post(
        "/api/v1/submissions",
        content="not-valid-json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_public_user_cannot_set_status_or_feedback(client):
    """Submissions cannot inject status or feedback in submission creation."""
    payload = {
        "title": "Attempted Exploit Project",
        "description": "Attempting to self-approve submission by including extra fields.",
        "domain": "Security",
        "github_url": "https://github.com/example/exploit-project",
        "demo_url": "https://demo.example.com",
        "status": "Approved",
        "feedback": "Self-approved by attacker",
    }
    # Extra fields are forbidden by schema
    response = client.post("/api/v1/submissions", json=payload)
    assert response.status_code == 422


def test_get_single_approved_submission(client, sample_submissions):
    """Public users can view an Approved submission."""
    approved_sub = [s for s in sample_submissions if s.status == "Approved"][0]
    response = client.get(f"/api/v1/submissions/{approved_sub.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == approved_sub.id
    assert data["status"] == "Approved"


def test_conceal_pending_and_rejected_from_public(client, sample_submissions):
    """Public users requesting Pending or Rejected submissions must receive 404 to avoid disclosure."""
    pending_sub = [s for s in sample_submissions if s.status == "Pending"][0]
    rejected_sub = [s for s in sample_submissions if s.status == "Rejected"][0]

    res_pending = client.get(f"/api/v1/submissions/{pending_sub.id}")
    assert res_pending.status_code == 404
    assert res_pending.json()["error"]["code"] == "NOT_FOUND"

    res_rejected = client.get(f"/api/v1/submissions/{rejected_sub.id}")
    assert res_rejected.status_code == 404
    assert res_rejected.json()["error"]["code"] == "NOT_FOUND"


def test_get_nonexistent_submission(client):
    """Querying a non-existent submission returns 404."""
    response = client.get("/api/v1/submissions/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


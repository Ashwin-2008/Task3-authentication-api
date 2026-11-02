def test_admin_approve_submission(client, admin_auth_headers, sample_submissions):
    """Admin can approve a pending submission with feedback remarks."""
    pending_sub = [s for s in sample_submissions if s.status == "Pending"][0]
    payload = {
        "status": "Approved",
        "feedback": "Project demonstrates excellent architecture and clean code.",
    }
    response = client.patch(
        f"/api/v1/admin/submissions/{pending_sub.id}/moderation",
        json=payload,
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == pending_sub.id
    assert data["status"] == "Approved"
    assert data["feedback"] == payload["feedback"]
    assert data["reviewed_at"] is not None

    # Verify that it is now visible to public users
    public_res = client.get(f"/api/v1/submissions/{pending_sub.id}")
    assert public_res.status_code == 200
    assert public_res.json()["status"] == "Approved"


def test_admin_reject_submission(client, admin_auth_headers, sample_submissions):
    """Admin can reject a submission with feedback remarks."""
    pending_sub = [s for s in sample_submissions if s.status == "Pending"][0]
    payload = {
        "status": "Rejected",
        "feedback": "GitHub repository returns 404 and live demo does not work.",
    }
    response = client.patch(
        f"/api/v1/admin/submissions/{pending_sub.id}/moderation",
        json=payload,
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == pending_sub.id
    assert data["status"] == "Rejected"
    assert data["feedback"] == payload["feedback"]

    # Verify that it is concealed from public users (404)
    public_res = client.get(f"/api/v1/submissions/{pending_sub.id}")
    assert public_res.status_code == 404


def test_moderation_via_post_alias(client, admin_auth_headers, sample_submissions):
    """Moderation route works identically using POST."""
    pending_sub = [s for s in sample_submissions if s.status == "Pending"][0]
    payload = {
        "status": "Approved",
        "feedback": "Approved via POST route.",
    }
    response = client.post(
        f"/api/v1/admin/submissions/{pending_sub.id}/moderation",
        json=payload,
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Approved"


def test_moderation_unauthenticated_blocked(client, sample_submissions):
    """Unauthenticated moderation requests are rejected with 401."""
    pending_sub = [s for s in sample_submissions if s.status == "Pending"][0]
    payload = {
        "status": "Approved",
        "feedback": "Unauthorized attempt",
    }
    response = client.patch(
        f"/api/v1/admin/submissions/{pending_sub.id}/moderation",
        json=payload,
    )
    assert response.status_code == 401


def test_moderation_invalid_status(client, admin_auth_headers, sample_submissions):
    """Submitting an invalid status is rejected with 422."""
    pending_sub = [s for s in sample_submissions if s.status == "Pending"][0]
    payload = {
        "status": "InvalidStatusChoice",
        "feedback": "Bad status",
    }
    response = client.patch(
        f"/api/v1/admin/submissions/{pending_sub.id}/moderation",
        json=payload,
        headers=admin_auth_headers,
    )
    assert response.status_code == 422


def test_moderation_nonexistent_submission(client, admin_auth_headers):
    """Moderating a non-existent submission returns 404."""
    payload = {
        "status": "Approved",
        "feedback": "Reviewing ghost submission",
    }
    response = client.patch(
        "/api/v1/admin/submissions/00000000-0000-0000-0000-000000000000/moderation",
        json=payload,
        headers=admin_auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


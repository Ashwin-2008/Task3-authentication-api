def test_public_listing_only_contains_approved(client, sample_submissions):
    """Public listing must never contain Pending or Rejected items."""
    response = client.get("/api/v1/submissions")
    assert response.status_code == 200
    data = response.json()
    items = data["items"]
    assert len(items) == 3
    for item in items:
        assert item["status"] == "Approved"


def test_search_by_title(client, sample_submissions):
    """Search query matching title filters correctly."""
    response = client.get("/api/v1/submissions?q=Irrigation")
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["total_items"] == 1
    assert data["items"][0]["title"] == "Smart Irrigation Network"


def test_search_by_description(client, sample_submissions):
    """Search query matching description filters correctly."""
    response = client.get("/api/v1/submissions?q=precision agriculture")
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["total_items"] == 1
    assert "Smart Irrigation" in data["items"][0]["title"]


def test_filter_by_domain(client, sample_submissions):
    """Domain filtering returns only items within specified domain."""
    response = client.get("/api/v1/submissions?domain=Agriculture")
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["total_items"] == 2
    for item in data["items"]:
        assert item["domain"] == "Agriculture"


def test_pagination_metadata(client, sample_submissions):
    """Pagination splits items accurately and produces correct metadata."""
    # We have 3 approved items; requesting limit=2 should return 2 on page 1
    response = client.get("/api/v1/submissions?page=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    pagination = data["pagination"]
    assert pagination["total_items"] == 3
    assert pagination["total_pages"] == 2
    assert pagination["current_page"] == 1
    assert pagination["page_size"] == 2
    assert pagination["has_next"] is True
    assert pagination["has_previous"] is False
    assert len(data["items"]) == 2

    # Request page 2
    response_p2 = client.get("/api/v1/submissions?page=2&limit=2")
    assert response_p2.status_code == 200
    data_p2 = response_p2.json()
    assert data_p2["pagination"]["current_page"] == 2
    assert data_p2["pagination"]["has_next"] is False
    assert data_p2["pagination"]["has_previous"] is True
    assert len(data_p2["items"]) == 1


def test_sorting(client, sample_submissions):
    """Sorting returns items ordered according to parameter."""
    response_asc = client.get("/api/v1/submissions?sort_by=title&sort_order=asc")
    assert response_asc.status_code == 200
    titles_asc = [item["title"] for item in response_asc.json()["items"]]
    assert titles_asc == sorted(titles_asc)

    response_desc = client.get("/api/v1/submissions?sort_by=title&sort_order=desc")
    assert response_desc.status_code == 200
    titles_desc = [item["title"] for item in response_desc.json()["items"]]
    assert titles_desc == sorted(titles_asc, reverse=True)


def test_empty_results_metadata(client):
    """Empty query results should return total_items=0 and total_pages=0."""
    response = client.get("/api/v1/submissions?q=NonExistentKeywordXYZ")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    pagination = data["pagination"]
    assert pagination["total_items"] == 0
    assert pagination["total_pages"] == 0
    assert pagination["has_next"] is False
    assert pagination["has_previous"] is False


def test_invalid_page_number(client):
    """Page number less than 1 should return 422 validation error."""
    response = client.get("/api/v1/submissions?page=0")
    assert response.status_code == 422


def test_invalid_limit_number(client):
    """Limit above 100 or below 1 should return 422 validation error."""
    res_high = client.get("/api/v1/submissions?limit=101")
    assert res_high.status_code == 422

    res_low = client.get("/api/v1/submissions?limit=0")
    assert res_low.status_code == 422


def test_public_user_status_filter_rejected(client):
    """Unauthenticated users attempting to filter by status are rejected with 401."""
    response = client.get("/api/v1/submissions?status=Pending")
    assert response.status_code == 401


def test_admin_can_view_all_statuses(client, admin_auth_headers, sample_submissions):
    """Admin can query submissions across all statuses via admin endpoint."""
    response = client.get("/api/v1/admin/submissions", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    # Total sample submissions: 3 approved, 1 pending, 1 rejected = 5
    assert data["pagination"]["total_items"] == 5

    # Admin filtering specifically for Pending
    res_pending = client.get("/api/v1/admin/submissions?status=Pending", headers=admin_auth_headers)
    assert res_pending.status_code == 200
    assert res_pending.json()["pagination"]["total_items"] == 1
    assert res_pending.json()["items"][0]["status"] == "Pending"


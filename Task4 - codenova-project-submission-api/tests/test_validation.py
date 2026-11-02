import pytest
from app.validators.urls import validate_github_url, validate_demo_url


class TestUrlValidation:
    """Test strict validation rules for GitHub and live demo URLs."""

    def test_valid_github_urls(self):
        valid_urls = [
            ("https://github.com/torvalds/linux", "https://github.com/torvalds/linux"),
            ("https://github.com/torvalds/linux/", "https://github.com/torvalds/linux"),
            ("https://github.com/fastapi/fastapi.git", "https://github.com/fastapi/fastapi"),
            ("https://github.com/owner-name/repo_123", "https://github.com/owner-name/repo_123"),
        ]
        for url, expected in valid_urls:
            assert validate_github_url(url) == expected

    def test_rejected_github_urls(self):
        invalid_urls = [
            "http://github.com/owner/repo",  # HTTP rejected
            "https://github.com.evil.example/owner/repo",  # Hostname spoofing
            "https://evil.example/github.com/owner/repo",  # Substring trick
            "https://notgithub.com/owner/repo",
            "javascript:alert(1)",
            "file:///etc/passwd",
            "not-a-url",
            "https://github.com",  # Missing owner and repo
            "https://github.com/onlyowner",  # Missing repo
            "https://user:pass@github.com/owner/repo",  # Embedded credentials
            "https://github.com:8080/owner/repo",  # Non-standard port
            "",
        ]
        for url in invalid_urls:
            with pytest.raises(ValueError):
                validate_github_url(url)

    def test_valid_demo_urls(self):
        valid_urls = [
            "https://example.com",
            "https://demo.example.com/app",
            "https://my-app.vercel.app/test?view=grid#section",
            "https://localhost:3000/demo",
        ]
        for url in valid_urls:
            result = validate_demo_url(url)
            assert result.startswith("https://")

    def test_rejected_demo_urls(self):
        invalid_urls = [
            "http://example.com",  # HTTP rejected
            "ftp://example.com",
            "javascript:alert(1)",
            "file:///etc/passwd",
            "https://user:password@example.com",  # Embedded credentials
            "https://",  # Missing host
            "not-a-valid-url",
            "",
        ]
        for url in invalid_urls:
            with pytest.raises(ValueError):
                validate_demo_url(url)


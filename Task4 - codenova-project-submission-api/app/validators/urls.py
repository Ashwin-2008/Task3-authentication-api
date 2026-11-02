import re
from urllib.parse import urlsplit, urlunsplit

GITHUB_REPO_PART_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.]+$")
HOSTNAME_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$|^localhost$"
)


def validate_github_url(url: str) -> str:
    """
    Strictly validate and normalize a GitHub repository URL.
    
    Accepts:
        - https://github.com/owner/repo
        - https://github.com/owner/repo/
        
    Rejects:
        - http schemes
        - Hostnames other than exactly 'github.com'
        - Missing owner or repo components
        - Embedded credentials
        - Dangerous schemes (javascript:, file:, etc.)
        - Arbitrary query/fragments or invalid characters
    """
    if not isinstance(url, str):
        raise ValueError("GitHub URL must be a string")

    cleaned_url = url.strip()
    if not cleaned_url:
        raise ValueError("GitHub URL cannot be empty")

    try:
        parsed = urlsplit(cleaned_url)
    except Exception as exc:
        raise ValueError(f"Malformed URL: {exc}") from exc

    # 1. Scheme check
    if parsed.scheme.lower() != "https":
        raise ValueError("GitHub URL must use the HTTPS scheme (e.g. https://github.com/...)")

    # 2. Hostname check
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("GitHub URL is missing a valid hostname")
    if hostname.lower() != "github.com":
        raise ValueError(f"GitHub URL hostname must be exactly 'github.com', got '{hostname}'")

    # 3. Credentials check
    if parsed.username or parsed.password:
        raise ValueError("Embedded credentials in GitHub URL are not permitted")

    # 4. Port check
    if parsed.port is not None and parsed.port != 443:
        raise ValueError("Custom ports are not permitted for GitHub repository URLs")

    # 5. Path check (must have owner and repository name)
    path_segments = [seg for seg in parsed.path.strip("/").split("/") if seg]
    if len(path_segments) != 2:
        raise ValueError(
            "GitHub URL must point to a specific repository in the format https://github.com/{owner}/{repo}"
        )

    owner, repo = path_segments[0], path_segments[1]

    # Clean potential .git suffix if present
    if repo.endswith(".git"):
        repo = repo[:-4]

    if not repo:
        raise ValueError("GitHub repository name cannot be empty")

    if not GITHUB_REPO_PART_REGEX.match(owner):
        raise ValueError(f"Invalid characters in GitHub repository owner '{owner}'")

    if not GITHUB_REPO_PART_REGEX.match(repo):
        raise ValueError(f"Invalid characters in GitHub repository name '{repo}'")

    # Normalize to canonical https://github.com/{owner}/{repo}
    normalized_url = f"https://github.com/{owner}/{repo}"
    return normalized_url


def validate_demo_url(url: str) -> str:
    """
    Strictly validate and normalize a live demo HTTPS URL.
    
    Accepts:
        - https://example.com
        - https://demo.example.com/app
        
    Rejects:
        - HTTP schemes
        - Missing or malformed hosts
        - Non-HTTPS or dangerous schemes
        - Embedded credentials
    """
    if not isinstance(url, str):
        raise ValueError("Demo URL must be a string")

    cleaned_url = url.strip()
    if not cleaned_url:
        raise ValueError("Demo URL cannot be empty")

    try:
        parsed = urlsplit(cleaned_url)
    except Exception as exc:
        raise ValueError(f"Malformed URL: {exc}") from exc

    # 1. Scheme check
    scheme = parsed.scheme.lower()
    if scheme == "http":
        raise ValueError("Live demo URL must use HTTPS; HTTP is not permitted")
    if scheme != "https":
        raise ValueError("Live demo URL must use the HTTPS scheme")

    # 2. Hostname check
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Live demo URL is missing a valid hostname")

    # Hostname pattern validation (standard domain or localhost)
    if not HOSTNAME_REGEX.match(hostname):
        raise ValueError(f"Live demo URL contains an invalid hostname: '{hostname}'")

    # 3. Credentials check
    if parsed.username or parsed.password:
        raise ValueError("Embedded credentials in demo URL are not permitted")

    # 4. Port check
    if parsed.port is not None:
        if not (1 <= parsed.port <= 65535):
            raise ValueError(f"Invalid port number: {parsed.port}")

    # Reconstruct normalized URL
    path = parsed.path
    normalized = urlunsplit((
        "https",
        parsed.netloc,
        path,
        parsed.query,
        parsed.fragment,
    ))
    return normalized

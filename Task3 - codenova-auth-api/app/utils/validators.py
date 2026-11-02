
import re


def validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters")

    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain an uppercase letter")

    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain a lowercase letter")

    if not re.search(r"\d", password):
        raise ValueError("Password must contain a digit")

    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("Password must contain a special character")

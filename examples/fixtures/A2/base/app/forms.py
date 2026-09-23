"""Validation for the signup form."""

import re

EMAIL = re.compile(r"^[^@\s]+@[^@\s]*$")


def validate_signup(email: str, password: str) -> list[str]:
    """Return the list of errors; empty when the form is valid."""
    errors = []
    if not EMAIL.match(email):
        errors.append("email: enter a valid address")
    if len(password) < 8:
        errors.append("password: use at least 8 characters")
    return errors

import unittest

from app.forms import validate_signup


class SignupTest(unittest.TestCase):
    def test_valid_signup(self):
        self.assertEqual(validate_signup("anna@example.com", "correct-horse"), [])

    def test_short_password(self):
        self.assertIn("password: use at least 8 characters", validate_signup("anna@example.com", "short"))


if __name__ == "__main__":
    unittest.main()

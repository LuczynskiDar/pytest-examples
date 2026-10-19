import re


class Customer:
    """A registered shop customer with a loyalty points balance."""

    EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")

    def __init__(self, name: str, email: str):
        if not name.strip():
            raise ValueError("Name cannot be empty")
        if not self.EMAIL_PATTERN.match(email):
            raise ValueError("Invalid email address")
        self.name = name.strip()
        self.email = email
        self.points = 0

    def add_points(self, points: int) -> None:
        if points <= 0:
            raise ValueError("Points must be positive")
        self.points += points

    def redeem_points(self, points: int) -> None:
        if points <= 0:
            raise ValueError("Points must be positive")
        if points > self.points:
            raise ValueError("Not enough points")
        self.points -= points

    def get_status(self) -> str:
        if self.points >= 1000:
            return "gold"
        if self.points >= 500:
            return "silver"
        return "standard"

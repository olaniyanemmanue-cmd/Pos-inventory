from werkzeug.security import generate_password_hash, check_password_hash
from models import User


class AuthManager:
    def __init__(self, db):
        self.db = db

    def create_user(self, username: str, password: str, role: str, full_name: str) -> bool:
        password_hash = generate_password_hash(password)
        try:
            self.db.execute(
                "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
                (username, password_hash, role, full_name),
            )
            return True
        except Exception:
            return False

    def authenticate(self, username: str, password: str) -> User:
        row = self.db.fetchone("SELECT * FROM users WHERE username = ?", (username,))
        if row and check_password_hash(row["password_hash"], password):
            return User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                role=row["role"],
                full_name=row["full_name"],
            )
        return None

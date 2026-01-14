from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str | bytes) -> str:
    if isinstance(password, bytes):
        password = password.decode("utf-8")
    return pwd_context.hash(password)

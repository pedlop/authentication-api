from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_encrypted_text(plain_text: str, hashed_text: str):
    return pwd_context.verify(plain_text, hashed_text)


def hash_encrypted_text(text: str):
    return pwd_context.hash(text)
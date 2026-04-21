from passlib.context import CryptContext

# 1. Initialize the Hashing Engine
# We use bcrypt because it is slow for hackers to crack but fast for us to use.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Takes a plain text password and returns a secure,
    one-way hashed string (the fingerprint).
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compares a typed password against the stored hash in the database.
    Returns True if they match, False if they don't.
    """
    return pwd_context.verify(plain_password, hashed_password)

import asyncio

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

ph = PasswordHasher()


async def hash_password(password: str) -> str:
    return await asyncio.to_thread(ph.hash, password=password)


async def verify_password(password: str, hashed: str) -> bool:
    try:
        await asyncio.to_thread(ph.verify, hashed, password)
        return True
    except (InvalidHashError, VerificationError):
        return False

# Plik: eventapi/infrastructure/utils/token.py
from datetime import datetime, timedelta, timezone
from pydantic import UUID4
from jose import JWTError, jwt
from fastapi import HTTPException
import logging

from eventapi.api.utils.enums import UserRole
from eventapi.infrastructure.utils.consts import (
    EXPIRATION_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_user_token(user_uuid: UUID4,user_role:UserRole) -> dict:
    """A function returning JWT token for user.

    Args:
        user_uuid (UUID5): The UUID of the user.

    Returns:
        dict: The token details.
        :param user_uuid:
        :param user_role:
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRATION_MINUTES)
    jwt_data = {
        "sub": str(user_uuid),
        "role": user_role.value,
        "exp": expire,
        "type": "confirmation"
    }
    print(f"JWT Data: {jwt_data}")  # Debug: Sprawdzenie danych tokena
    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return {"user_token": encoded_jwt, "expires": expire}

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {payload}")  # Debug: Zawartość dekodowanego tokena
        return payload
    except JWTError as e:
        print(f"Token decoding failed: {str(e)}")  # Debug: Błąd dekodowania
        raise HTTPException(status_code=401, detail="Invalid or expired token")
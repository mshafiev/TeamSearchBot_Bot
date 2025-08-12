from typing import Optional, Tuple
import re

MAX_MESSAGE_LENGTH: int = 1000


def is_valid_user_id(user_id: Optional[str]) -> bool:
    if not user_id:
        return False
    return bool(re.fullmatch(r"\d{1,20}", str(user_id)))


def validate_message_text(text: Optional[str]) -> Tuple[bool, Optional[str]]:
    if text is None:
        return False, None
    text = text.strip()
    if not text:
        return False, None
    if len(text) > MAX_MESSAGE_LENGTH:
        return False, text[:MAX_MESSAGE_LENGTH]
    return True, text


def parse_age(text: str) -> Optional[int]:
    try:
        age = int(text)
        if 14 <= age <= 100:
            return age
        return None
    except Exception:
        return None


def parse_date_dmy(text: str) -> Optional[Tuple[int, int, int]]:
    try:
        parts = text.split("-")
        if len(parts) != 3:
            return None
        day, month, year = map(int, parts)
        if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100:
            return day, month, year
        return None
    except Exception:
        return None
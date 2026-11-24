"""Row validation: airport list loading, single-row checks, record building."""

from datetime import datetime
import math
import re

_FLIGHT_ID_RE = re.compile(r"[A-Za-z0-9]{2,8}", re.ASCII)
_AIRPORT_RE = re.compile(r"[A-Z]{3}", re.ASCII)
_DATETIME_RE = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", re.ASCII)
_DATETIME_FMT = "%Y-%m-%d %H:%M"


def is_valid_datetime_str(value: str) -> bool:
    """Return True iff value is an exact YYYY-MM-DD HH:MM calendar date/time."""
    if len(value) != 16 or _DATETIME_RE.fullmatch(value) is None:
        return False
    try:
        datetime.strptime(value, _DATETIME_FMT)
    except ValueError:
        return False
    return True


def parse_datetime_str(value: str) -> datetime:
    """Parse a validated YYYY-MM-DD HH:MM string into a datetime object."""
    return datetime.strptime(value, _DATETIME_FMT)


def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    airports: set[str] = set()
    with open(path, mode="r", encoding="utf-8") as f:
        for line in f:
            code = line.strip()
            if not code or code.startswith("#"):
                continue
            airports.add(code)
    return airports


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    stripped = [col.strip() for col in fields]
    flight_id, origin, destination, dep_str, arr_str, price_str = stripped

    if any(val == "" for val in stripped):
        return "MISSING_FIELD"

    if _FLIGHT_ID_RE.fullmatch(flight_id) is None:
        return "INVALID_FLIGHT_ID"

    if _AIRPORT_RE.fullmatch(origin) is None or origin not in airports:
        return "INVALID_ORIGIN"

    if _AIRPORT_RE.fullmatch(destination) is None or destination not in airports:
        return "INVALID_DESTINATION"

    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    if not is_valid_datetime_str(dep_str):
        return "INVALID_DEPARTURE"

    if not is_valid_datetime_str(arr_str):
        return "INVALID_ARRIVAL"

    if parse_datetime_str(arr_str) <= parse_datetime_str(dep_str):
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price_val = float(price_str)
    except ValueError:
        return "INVALID_PRICE"
    if not math.isfinite(price_val):
        return "INVALID_PRICE"

    if price_val <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    flight_id, origin, destination, dep_str, arr_str, price_str = [
        col.strip() for col in fields
    ]
    return {
        "flight_id": flight_id,
        "origin": origin,
        "destination": destination,
        "departure_datetime": dep_str,
        "arrival_datetime": arr_str,
        "price": float(price_str),
    }

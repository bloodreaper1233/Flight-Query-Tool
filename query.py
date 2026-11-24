"""Running queries against the flight database."""

import math

from validator import is_valid_datetime_str, parse_datetime_str

_ALLOWED_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
    "min_price",
    "sort_by",
    "order",
    "limit",
}
_RECORD_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
}
_SORT_ORDERS = {"asc", "desc"}


def _is_valid_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _is_valid_query(query: object) -> bool:
    if not isinstance(query, dict):
        return False

    if not set(query.keys()).issubset(_ALLOWED_KEYS):
        return False

    if "order" in query and "sort_by" not in query:
        return False

    for key in ("flight_id", "origin", "destination"):
        if key in query and not isinstance(query[key], str):
            return False

    for key in ("departure_datetime", "arrival_datetime"):
        if key in query:
            val = query[key]
            if not isinstance(val, str) or not is_valid_datetime_str(val):
                return False

    for key in ("price", "min_price"):
        if key in query and not _is_valid_number(query[key]):
            return False

    if "sort_by" in query:
        if not isinstance(query["sort_by"], str) or query["sort_by"] not in _RECORD_KEYS:
            return False

    if "order" in query:
        if not isinstance(query["order"], str) or query["order"] not in _SORT_ORDERS:
            return False

    if "limit" in query:
        lim = query["limit"]
        if not isinstance(lim, int) or isinstance(lim, bool) or lim < 0:
            return False

    return True


def _matches_filters(record: dict, query: dict) -> bool:
    if "flight_id" in query and record["flight_id"] != query["flight_id"]:
        return False
    if "origin" in query and record["origin"] != query["origin"]:
        return False
    if "destination" in query and record["destination"] != query["destination"]:
        return False
    if "departure_datetime" in query:
        if parse_datetime_str(record["departure_datetime"]) < parse_datetime_str(
            query["departure_datetime"]
        ):
            return False
    if "arrival_datetime" in query:
        if parse_datetime_str(record["arrival_datetime"]) > parse_datetime_str(
            query["arrival_datetime"]
        ):
            return False
    if "price" in query and record["price"] > query["price"]:
        return False
    if "min_price" in query and record["price"] < query["min_price"]:
        return False
    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    if not _is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = [rec for rec in db if _matches_filters(rec, query)]

    if "sort_by" in query:
        sort_key = query["sort_by"]
        reverse = query.get("order", "asc") == "desc"
        matches = sorted(matches, key=lambda rec: rec[sort_key], reverse=reverse)

    if "limit" in query:
        matches = matches[: query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, list):
        return [run_query(db, q) for q in queries]
    return [run_query(db, queries)]
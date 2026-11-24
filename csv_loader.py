"""Reading CSV files into flight records and error messages."""

import csv
import os

from validator import to_record, validate_row


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """
    records: list[dict] = []
    errors: list[str] = []
    seen_flights: set[tuple[str, str]] = set()

    for path in paths:
        base_name = os.path.basename(path)
        with open(path, mode="r", encoding="utf-8", newline="") as f:
            for line_no, raw_line in enumerate(f, start=1):
                if line_no == 1:
                    continue

                if not raw_line.strip() or raw_line.lstrip().startswith("#"):
                    continue

                raw_text = raw_line.rstrip("\r\n")
                parsed_rows = list(csv.reader([raw_line]))
                fields = parsed_rows[0] if parsed_rows else []

                err_code = validate_row(fields, airports)
                if err_code is not None:
                    errors.append(f"{base_name}:{line_no}: {err_code} | {raw_text}")
                    continue

                record = to_record(fields)
                flight_key = (record["flight_id"], record["departure_datetime"])
                if flight_key in seen_flights:
                    errors.append(
                        f"{base_name}:{line_no}: DUPLICATE_FLIGHT | {raw_text}"
                    )
                    continue

                seen_flights.add(flight_key)
                records.append(record)

    return records, errors

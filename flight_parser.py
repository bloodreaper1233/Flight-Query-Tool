"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""

import argparse
from datetime import datetime
import json
import logging
import os
import sys

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

STUDENT_ID = "251ADB018"
FIRST_NAME = "Joyal"
LAST_NAME = "Joshy"


class _ArgumentParserError(Exception):
    """Internal exception used to turn argparse errors into exit code 2."""


class _StrictArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise _ArgumentParserError(message)


def _build_parser() -> _StrictArgumentParser:
    parser = _StrictArgumentParser(
        prog="flight_parser.py",
        description="Validate flight CSV schedules, build a JSON database, and run queries.",
    )
    parser.add_argument("-i", dest="input_file", help="Parse a single CSV file.")
    parser.add_argument(
        "-d", dest="input_dir", help="Parse every .csv file in a folder."
    )
    parser.add_argument(
        "-j", dest="json_db", help="Load an existing JSON database file."
    )
    parser.add_argument("-a", dest="airports_file", help="Airport list file.")
    parser.add_argument(
        "-o",
        dest="output_db",
        default=None,
        help="Output path for JSON database (default: db.json).",
    )
    parser.add_argument("-q", dest="query_file", help="JSON query file to run.")
    parser.add_argument(
        "-r",
        dest="response_dir",
        default=".",
        help="Folder for query response file (default: current directory).",
    )
    return parser


def _setup_logger(log_path: str) -> tuple[logging.Logger, logging.Handler]:
    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    logger.addHandler(handler)
    return logger, handler


def _cleanup_logger(logger: logging.Logger, handler: logging.Handler | None) -> None:
    if handler is not None:
        logger.removeHandler(handler)
        handler.close()


def _fail(message: str, logger: logging.Logger | None = None) -> int:
    err_line = f"Error: {message}"
    if logger is not None and logger.handlers:
        logger.error(err_line)
    print(err_line, file=sys.stderr)
    return 1


def _collect_csv_paths(folder: str) -> list[str]:
    if not os.path.isdir(folder):
        raise OSError(f"Folder does not exist or is not a directory: {folder}")
    try:
        entries = os.listdir(folder)
    except OSError as exc:
        raise OSError(f"Cannot read folder {folder}: {exc}") from exc

    csv_files = sorted(
        name
        for name in entries
        if name.endswith(".csv") and os.path.isfile(os.path.join(folder, name))
    )
    if not csv_files:
        raise OSError(f"No .csv files found in folder: {folder}")
    return [os.path.join(folder, name) for name in csv_files]


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except _ArgumentParserError as exc:
        print(f"usage: {parser.prog} [-h] ...", file=sys.stderr)
        print(f"{parser.prog}: error: {exc}", file=sys.stderr)
        return 2

    sources = [
        flag
        for flag, val in (("-i", args.input_file), ("-d", args.input_dir), ("-j", args.json_db))
        if val is not None
    ]
    if len(sources) == 0:
        print(
            f"{parser.prog}: error: one of -i, -d, or -j is required",
            file=sys.stderr,
        )
        return 2
    if len(sources) > 1:
        print(
            f"{parser.prog}: error: -i, -d, and -j are mutually exclusive",
            file=sys.stderr,
        )
        return 2

    is_csv_mode = args.input_file is not None or args.input_dir is not None
    if is_csv_mode and not args.airports_file:
        print(
            f"{parser.prog}: error: -a is required with -i or -d",
            file=sys.stderr,
        )
        return 2

    if not is_csv_mode and args.output_db is not None:
        print(
            f"{parser.prog}: error: -o is only allowed with -i or -d",
            file=sys.stderr,
        )
        return 2

    logger: logging.Logger | None = None
    handler: logging.Handler | None = None

    try:
        if is_csv_mode:
            output_db_path = args.output_db if args.output_db is not None else "db.json"
            out_dir = os.path.dirname(output_db_path) or "."
            if not os.path.isdir(out_dir):
                return _fail(f"Output directory does not exist: {out_dir}")

            log_path = os.path.join(out_dir, "errors.log")
            try:
                logger, handler = _setup_logger(log_path)
            except OSError as exc:
                return _fail(f"Cannot open log file {log_path}: {exc}")

            try:
                airports = load_airports(args.airports_file)
                if args.input_file is not None:
                    if not os.path.isfile(args.input_file):
                        return _fail(
                            f"Input CSV file does not exist: {args.input_file}",
                            logger,
                        )
                    csv_paths = [args.input_file]
                else:
                    csv_paths = _collect_csv_paths(args.input_dir)

                records, errors = parse_files(csv_paths, airports)
            except OSError as exc:
                return _fail(str(exc), logger)

            for err_msg in errors:
                logger.warning(err_msg)

            try:
                with open(output_db_path, mode="w", encoding="utf-8") as f:
                    json.dump(records, f, indent=2)
                    f.write("\n")
            except OSError as exc:
                return _fail(
                    f"Cannot write database file {output_db_path}: {exc}", logger
                )

            db = records
        else:
            try:
                with open(args.json_db, mode="r", encoding="utf-8") as f:
                    loaded_db = json.load(f)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
                return _fail(f"Cannot load JSON database {args.json_db}: {exc}")

            if not isinstance(loaded_db, list) or not all(
                isinstance(item, dict) for item in loaded_db
            ):
                return _fail(
                    f"JSON database {args.json_db} must be a JSON array of objects"
                )
            db = loaded_db

        if args.query_file is not None:
            if not os.path.isdir(args.response_dir):
                return _fail(
                    f"Response directory does not exist: {args.response_dir}", logger
                )

            try:
                with open(args.query_file, mode="r", encoding="utf-8") as f:
                    queries = json.load(f)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
                return _fail(
                    f"Cannot load query file {args.query_file}: {exc}", logger
                )

            if not isinstance(queries, (dict, list)):
                return _fail(
                    f"Query file {args.query_file} must contain a JSON object or array",
                    logger,
                )

            results = run_queries(db, queries)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            response_filename = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp}.json"
            )
            response_path = os.path.join(args.response_dir, response_filename)

            try:
                with open(response_path, mode="w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2)
                    f.write("\n")
            except OSError as exc:
                return _fail(
                    f"Cannot write response file {response_path}: {exc}", logger
                )

        return 0
    finally:
        if logger is not None:
            _cleanup_logger(logger, handler)


if __name__ == "__main__":
    sys.exit(main())

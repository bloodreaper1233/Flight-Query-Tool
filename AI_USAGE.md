# AI Usage Disclosure

## Tools used

- Gemini (AI assistant)

## What I used them for

- Checking specific logic details, edge cases, and error handling across the modules
- Running through CLI commands, running the public test suite in GitHub Codespaces, and verifying repository layout before pushing

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| --- | --- | --- |
| `validator.py` | Validation and record formatting logic | Explained and reviewed |
| `csv_loader.py` | `parse_files` | Reviewed |
| `query.py` | Query filtering, sorting, and limit logic | Explained and reviewed |
| `flight_parser.py` | CLI flags, logging, and file handling | Reviewed |

## Key prompts

1. Asked quick questions to double-check validation rules, CSV/query behavior, and CLI edge cases.
2. Checked commands for running the public tests and verifying the GitHub repository structure before submission.

## What I changed or verified myself

I wrote and adjusted the project files, added them to my GitHub repository, pulled them into GitHub Codespaces, ran `python3 tests/run_public_tests.py` (passing all 29 public tests), tested CLI exit codes manually, and verified the required files and student constants (`STUDENT_ID`, `FIRST_NAME`, `LAST_NAME`) before committing and pushing.
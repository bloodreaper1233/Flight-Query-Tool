# AI Usage Disclosure

## Tools used

- Gemini (AI assistant)

## Conversation links

- Link 1: https://gemini.google.com/app/0a625761671559ee

## What I used them for

- Checking errors and debugging issues across the project files
- Generating small code snippets and boilerplate examples to understand patterns and structure
- Explaining logic, edge cases, CLI argument handling, and logging behavior so I could understand how the code works

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| --- | --- | --- |
| `validator.py` | Validation and record formatting logic | Explained, reviewed, and modified |
| `csv_loader.py` | `parse_files` | Generated snippets, explained, and modified |
| `query.py` | Query filtering, sorting, and limit logic | Explained, reviewed, and modified |
| `flight_parser.py` | CLI flags, logging, and file handling | Generated reference code, explained, and modified |

## Key prompts

1. Asked for help checking errors, understanding logic/edge cases, and generating small code examples to see how parts work.
2. Asked for a reference structure for `flight_parser.py` covering `argparse`, `errors.log` setup/teardown, and exit codes (`0`, `1`, `2`), and reviewed how it fits the assignment.
3. Checked commands for running the public test suite and verifying repository files before pushing.

## What I changed or verified myself

I reviewed the generated snippets and explanations to make sure I understood how each part works, adapted and integrated the changes into the project files, updated my student details (`STUDENT_ID`, `FIRST_NAME`, `LAST_NAME`), ran `python3 tests/run_public_tests.py` (passing all 29 public tests), tested CLI exit codes manually, and verified the repository before committing and pushing.
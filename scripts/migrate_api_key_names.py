"""Rename one-letter local API-key aliases without exposing their values."""

import argparse
from pathlib import Path

NAMES = {
    "a": "ALIO_PLUS_FACILITY_API_KEY",
    "b": "ALIO_PLUS_EVENT_API_KEY",
    "c": "ALIO_PLUS_BUSINESS_API_KEY",
    "d": "ALIO_PLUS_ORGANIZATION_API_KEY",
    "e": "MPM_PUBLIC_EMPLOYMENT_API_KEY",
}


def migrate(path: Path, blank_values: bool) -> list[str]:
    original = path.read_text(encoding="utf-8")
    output: list[str] = []
    migrated: list[str] = []
    for line in original.splitlines(keepends=True):
        key, separator, value = line.partition("=")
        normalized_key = key.strip()
        if separator and normalized_key in NAMES:
            replacement_value = "\n" if blank_values else value
            output.append(f"{NAMES[normalized_key]}={replacement_value}")
            migrated.append(NAMES[normalized_key])
        else:
            output.append(line)
    path.write_text("".join(output), encoding="utf-8")
    return migrated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default=".env")
    parser.add_argument("--example", default=".env.example")
    args = parser.parse_args()
    env_names = migrate(Path(args.env), blank_values=False)
    example_names = migrate(Path(args.example), blank_values=True)
    print({"env_renamed": env_names, "example_renamed_and_blank": example_names})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

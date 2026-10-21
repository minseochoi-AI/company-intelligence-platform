"""Excel link formatting, independent of URL reachability or job status."""

import re


def generate_clickable_hyperlink(
    target_col: str, row_idx: int, label: str = "공고 확인 ↗"
) -> str:
    if (
        not re.fullmatch("[A-Z]{1,3}", target_col)
        or type(row_idx) is not int
        or not 1 <= row_idx <= 1048576
    ):
        raise ValueError("invalid Excel cell reference")
    return f'=HYPERLINK({target_col}{row_idx}, "{label.replace(chr(34), chr(34) * 2)}")'

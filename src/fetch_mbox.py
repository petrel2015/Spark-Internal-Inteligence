"""Fetch a Spark dev-list mbox archive from Apache Pony Mail.

Apache mailing lists are archived by Pony Mail (Foal). The "Download as mbox"
button on https://lists.apache.org/list?dev@spark.apache.org:YYYY-M simply
calls the backend API:

    https://lists.apache.org/api/mbox.lua?list=dev&domain=spark.apache.org&d=YYYY-M

This module hits that API directly - no browser, no Selenium. Standard library
only, so it works in the same venv as the rest of the project.
"""

import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from rich import print

PONYMAIL_API = "https://lists.apache.org/api/mbox.lua"


def fetch_mbox(year_month: str, output_dir: Path = Path("input")) -> Path:
    """Download the Spark dev-list mbox for a given YYYY-M string.

    Args:
        year_month: Month identifier like ``"2026-7"`` or ``"2025-10"``.
            Matches the Pony Mail URL convention (no zero-padding required).
        output_dir: Directory to save the .mbox file. Created if missing.

    Returns:
        The path to the downloaded .mbox file.

    Raises:
        ValueError: if year_month doesn't look like YYYY-M or YYYY-MM.
        URLError / HTTPError: if the download fails.
    """
    # Validate the input loosely - accept "2026-7" and "2025-10".
    parts = year_month.split("-")
    if len(parts) != 2 or not (parts[0].isdigit() and parts[1].isdigit()):
        raise ValueError(
            f"Invalid month {year_month!r}, expected YYYY-M or YYYY-MM (e.g. '2026-7')"
        )

    params = urlencode(
        {"list": "dev", "domain": "spark.apache.org", "d": year_month}
    )
    url = f"{PONYMAIL_API}?{params}"

    output_dir.mkdir(parents=True, exist_ok=True)
    # Normalize to YYYY_MM for the filename, matching the repo's existing sample
    # name dev_spark_apache_org_2025-10.mbox.
    filename = f"dev_spark_apache_org_{year_month}.mbox"
    dest = output_dir / filename

    print(f"Downloading mbox for {year_month} from Apache Pony Mail...")
    req = Request(url, headers={"User-Agent": "spark-internal-intelligence/1.0"})
    try:
        with urlopen(req, timeout=60) as resp:
            data = resp.read()
    except HTTPError as e:
        print(f"[bold red]HTTP error {e.code}[/bold red]: {e.reason}")
        print(f"  URL: {url}")
        sys.exit(1)
    except URLError as e:
        print(f"[bold red]Network error[/bold red]: {e.reason}")
        sys.exit(1)

    dest.write_bytes(data)

    # Sanity check: a valid mbox starts with a "From " line.
    if not data.startswith(b"From "):
        print(
            f"[bold yellow]Warning[/bold yellow]: {dest} does not start with a "
            "'From ' line - the download may not be a valid mbox."
        )

    msg_count = data.count(b"\nFrom ")
    print(
        f"[bold green]Saved[/bold green] {dest} "
        f"({len(data):,} bytes, ~{msg_count} messages)"
    )
    return dest


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m src.fetch_mbox <YYYY-M>")
        print("  e.g. python -m src.fetch_mbox 2026-7")
        sys.exit(1)
    fetch_mbox(sys.argv[1])

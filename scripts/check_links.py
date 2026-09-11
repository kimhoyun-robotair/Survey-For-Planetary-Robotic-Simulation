"""Record public link responses without changing the paper's classifications."""

import pprint
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))

from scripts.catalog import SURVEY
from scripts.models import LinkCheck


def check(url: str) -> LinkCheck:
    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    result: LinkCheck = {"url": url, "checked_at": checked_at, "http_status": None,
              "final_url": None, "status": "request_failed", "confirmed_reachable_on": None}
    request = Request(url, headers={"User-Agent": "PlanetarySurvey-LinkCheck/1.0"})
    try:
        with urlopen(request, timeout=18) as response:
            body = response.read(250_000).decode("utf-8", errors="replace")
            result["http_status"] = response.status
            result["final_url"] = response.url
            challenge = re.search(
                r"<title[^>]*>[^<]*(?:just a moment|access denied|attention required|robot check|verifying your browser|security check)",
                body, re.I)
            result["status"] = ("access_restricted" if challenge else "reachable"
                                if response.status == 200 and len(body.strip()) > 500
                                else "response_unconfirmed")
            if result["status"] == "reachable":
                result["confirmed_reachable_on"] = checked_at[:10]
    except HTTPError as error:
        result["http_status"] = error.code
        result["final_url"] = error.url
        result["status"] = ("access_restricted" if error.code in (401, 403, 429)
                            else "not_found" if error.code in (404, 410) else "request_failed")
    except (URLError, TimeoutError, ConnectionError):
        pass
    return result


def main() -> None:
    survey = SURVEY
    records = survey["works"] + survey["additional_works"]
    urls = sorted({url for record in records
                   for url in (record["publication_url"], record["resource_url"]) if url})
    with ThreadPoolExecutor(max_workers=5) as pool:
        checks = list(pool.map(check, urls))
    output = ('"""Dated public resource responses used by the page builder."""\n\n'
              'from scripts.models import LinkCheck\n\nCHECKS: list[LinkCheck] = '
              + pprint.pformat(checks, width=110, sort_dicts=False) + "\n")
    (ROOT / "scripts/link_status.py").write_text(output, encoding="utf-8")
    for status in sorted({item["status"] for item in checks}):
        print(f"{status}: {sum(item['status'] == status for item in checks)}")


if __name__ == "__main__":
    main()

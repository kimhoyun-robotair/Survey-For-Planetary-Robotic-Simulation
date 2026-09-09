"""Record public link responses without changing the paper's classifications."""

import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def check(url: str) -> dict:
    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    result = {"url": url, "checked_at": checked_at, "http_status": None,
              "final_url": None, "status": "request_failed", "confirmed_reachable_on": None}
    request = Request(url, headers={"User-Agent": "PlanetarySurvey-LinkCheck/1.0"})
    try:
        with urlopen(request, timeout=18) as response:
            body = response.read(250_000).decode("utf-8", errors="replace")
            result["http_status"] = response.status
            result["final_url"] = response.url
            challenge = re.search(r"<title[^>]*>[^<]*(?:just a moment|access denied|attention required|robot check)", body, re.I)
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
    survey = json.loads((ROOT / "data/survey.json").read_text())
    records = survey["works"] + survey["additional_works"]
    urls = sorted({record[field] for record in records for field in ("publication_url", "resource_url") if record[field]})
    with ThreadPoolExecutor(max_workers=5) as pool:
        checks = list(pool.map(check, urls))
    result = {"schema_version": 1, "method": "Unauthenticated HTTP GET; response and access checks only. No installation, simulation, or reproduction test.", "checks": checks}
    (ROOT / "data/link-checks.json").write_text(json.dumps(result, indent=2) + "\n")
    for status in sorted({item["status"] for item in checks}):
        print(f"{status}: {sum(item['status'] == status for item in checks)}")


if __name__ == "__main__":
    main()

"""Build the static companion and downloads from the curated public records."""

import csv
import html
import json
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
STATUS = {
    "reachable": "HTTP reachable",
    "access_restricted": "Access restricted",
    "response_unconfirmed": "Response unconfirmed",
    "not_found": "Missing-page response",
    "request_failed": "Request failed",
}
DOMAIN = {"Planet.": "Planetary / generic", "Lu./Ma.": "Lunar / Mars", "Ma./Lu.": "Mars / Lunar"}


def esc(value: object) -> str:
    return html.escape(str(value))


def validate(survey: dict, checks: list[dict]) -> None:
    works = survey["works"]
    if len(works) != 22 or len({w["id"] for w in works}) != 22:
        raise ValueError("The paper dataset must contain 22 uniquely identified works.")
    if Counter(w["access_as_reported"] for w in works) != {"Direct": 12, "Request": 1, "No release listed": 9}:
        raise ValueError("Access counts must match the paper baseline.")
    if Counter(w["platform_group"] for w in works) != {"Rover-relevant": 16, "Construction": 3, "Aerial": 2, "Multi-platform": 1}:
        raise ValueError("Platform counts must match the paper baseline.")
    date.fromisoformat(survey["updated_on"])
    urls = {r[field] for r in works + survey["additional_works"]
            for field in ("publication_url", "resource_url") if r[field]}
    if {c["url"] for c in checks} != urls or len(checks) != len(urls):
        raise ValueError("Every listed external resource needs exactly one check record.")
    for check in checks:
        if check["status"] not in STATUS:
            raise ValueError("Unknown link-check status.")
        datetime.fromisoformat(check["checked_at"])
        if check["confirmed_reachable_on"] and check["status"] != "reachable":
            raise ValueError("An unsuccessful check cannot claim confirmed reachability.")
        for url in (check["url"], check["final_url"]):
            if url:
                parsed = urlparse(url)
                if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                    raise ValueError("Only public HTTPS resource URLs are allowed.")


def result_label(check: dict) -> str:
    code = f" · HTTP {check['http_status']}" if check["http_status"] else ""
    return STATUS[check["status"]] + code


def resource(label: str, url: str | None, checks: dict) -> str:
    if not url:
        return f'<div class="resource-block"><h4>{esc(label)}</h4><p class="check-meta">No link recorded in the paper.</p></div>'
    check = checks[url]
    checked = check["checked_at"][:10]
    confirmed = check["confirmed_reachable_on"] or "Not confirmed in this check"
    return (f'<div class="resource-block"><h4>{esc(label)}</h4>'
            f'<a class="resource-url" href="{esc(url)}">{esc(url)}</a>'
            f'<p class="check-meta">Last checked: <time datetime="{esc(checked)}">{esc(checked)}</time> (UTC)'
            f'<br>{esc(result_label(check))}<br>Confirmed reachable: {esc(confirmed)}</p></div>')


def record(work: dict, checks: dict) -> str:
    domain = DOMAIN.get(work["domain"], work["domain"])
    domain_group = "Cross-domain" if work["domain"] in DOMAIN else domain
    access = work["access_as_reported"]
    badge_class = "badge-direct" if access == "Direct" else "badge-request" if access == "Request" else ""
    bib = work["bibliography"]
    searchable = " ".join(str(v) for v in [work["name"], work["year"], domain,
                         work["category"], work["platform_group"], work["engine"], work["ros"],
                         work["terrain"], work["sensors"], bib["title"], bib["author"]] if v).lower()
    fields = [("Reported category", work["category"]), ("Engine / tool", work["engine"]),
              ("ROS support", work["ros"] or "Not reported"), ("Terrain source", work["terrain"] or "Not reported"),
              ("Sensors / outputs", work["sensors"]), ("Paper reference", f"[{work['paper_reference']}] · Table I, p. 4")]
    profile = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in fields)
    venue = bib["journal"] or bib["booktitle"] or ("arXiv:" + bib["eprint"] if bib["eprint"] else "Venue not specified in the bibliography")
    note = f'<p class="record-note">{esc(work["note"])}</p>' if work["note"] else ""
    return (f'<details class="record" id="work-{esc(work["id"])}" data-search="{esc(searchable)}" '
            f'data-domain="{esc(domain_group)}" data-platform="{esc(work["platform_group"])}" data-access="{esc(access)}">'
            f'<summary><span class="record-name">{esc(work["name"])}</span><span class="record-year">{work["year"]}</span>'
            f'<span class="record-domain">{esc(domain)}</span><span class="record-category">{esc(work["category"])}</span>'
            f'<span class="badge {badge_class}">{esc(access)}</span></summary><div class="record-body">'
            f'<h3 class="record-title">{esc(bib["title"])}</h3><p class="reference-line">{esc(bib["author"].replace(" and others", " et al."))} · {esc(venue)} · {work["year"]}</p>'
            f'<dl class="profile-fields">{profile}</dl><div class="resource-grid">'
            + resource("Scholarly source", work["publication_url"], checks)
            + resource(work["resource_type"] or "Study artifact", work["resource_url"], checks)
            + f'</div>{note}<p class="evidence-line">Evidence: {esc(work["evidence"])}</p></div></details>')


def related(work: dict, checks: dict) -> str:
    return (f'<article class="related-work" id="related-{esc(work["id"])}"><div><span class="badge">{esc(work["status"])}</span>'
            f'<h3>{esc(work["name"])}</h3><p class="related-year">{work["year"]}</p></div><div class="related-content">'
            f'<p class="record-title">{esc(work["title"])}</p><p>{esc(work["scope_note"])}</p><p>{esc(work["decision_note"])}</p>'
            f'<p class="historical-note">Original exclusion reason: {esc(work["historical_reason"] or "Not recorded in the available screening materials.")} '
            f'Companion note reviewed: {esc(work["reviewed_on"])}. Basis: {esc(work["basis"])}</p><div class="resource-grid">'
            + resource("Scholarly source", work["publication_url"], checks)
            + (resource("Repository", work["resource_url"], checks) if work["resource_url"] else "")
            + '</div></div></article>')


def downloads(works: list[dict], checks: dict) -> None:
    rows = []
    bibliography = []
    for work in works:
        bib = work["bibliography"]
        row = {k: work[k] for k in ("id", "name", "year", "domain", "category", "platform_group", "engine", "ros",
                                  "access_as_reported", "terrain", "sensors", "publication_url", "resource_url",
                                  "resource_type", "paper_reference", "evidence", "note")}
        row.update({k: bib[k] for k in ("title", "author", "doi", "eprint")})
        for prefix in ("publication", "resource"):
            check = checks.get(work[prefix + "_url"], {})
            row[prefix + "_last_checked"] = check.get("checked_at")
            row[prefix + "_check_result"] = check.get("status")
            row[prefix + "_confirmed_reachable_on"] = check.get("confirmed_reachable_on")
        rows.append(row)
        kind = "article" if bib["journal"] else "inproceedings" if bib["booktitle"] else "misc"
        fields = {k: v for k, v in bib.items() if v}
        if bib["eprint"]:
            fields["archivePrefix"] = "arXiv"
        if work["publication_url"]:
            fields["url"] = work["publication_url"]
        entries = ",\n".join(f"  {key} = {{{value}}}" for key, value in fields.items())
        bibliography.append(f"@{kind}{{{work['id']},\n{entries}\n}}")
    with (ROOT / "data/survey.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / "data/references.bib").write_text("\n\n".join(bibliography) + "\n", encoding="utf-8")


def main() -> None:
    survey = json.loads((ROOT / "data/survey.json").read_text(encoding="utf-8"))
    check_data = json.loads((ROOT / "data/link-checks.json").read_text(encoding="utf-8"))
    validate(survey, check_data["checks"])
    checks = {c["url"]: c for c in check_data["checks"]}
    html_template = (ROOT / "templates/index.html").read_text(encoding="utf-8")
    totals = Counter(c["status"] for c in checks.values())
    summary = f'<p><strong>{len(checks)}</strong> links checked</p>' + "".join(
        f'<p><strong>{number}</strong> {esc(STATUS[status].lower())}</p>' for status, number in sorted(totals.items()))
    check_rows = "".join(f'<tr><td><a href="{esc(c["url"])}">{esc(c["url"])}</a></td>'
                         f'<td><time datetime="{esc(c["checked_at"])}">{esc(c["checked_at"][:10])}</time></td>'
                         f'<td>{esc(result_label(c))}</td><td>{esc(c["confirmed_reachable_on"] or "Not confirmed")}</td></tr>'
                         for c in checks.values())
    replacements = {"@@UPDATED@@": esc(survey["updated_on"]),
                    "@@RECORDS@@": "\n".join(record(w, checks) for w in survey["works"]),
                    "@@RELATED@@": "\n".join(related(w, checks) for w in survey["additional_works"]),
                    "@@CHECK_SUMMARY@@": summary, "@@CHECK_ROWS@@": check_rows}
    for token, value in replacements.items():
        html_template = html_template.replace(token, value)
    (ROOT / "index.html").write_text(html_template, encoding="utf-8")
    downloads(survey["works"], checks)
    print(f"Built index.html, 22 CSV/BibTeX records, and {len(checks)} visible link checks.")


if __name__ == "__main__":
    main()

"""Validate the curated records and build the static project page."""

import html
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))

from scripts.catalog import SURVEY
from scripts.link_status import CHECKS
from scripts.models import LinkCheck, RelatedWork, Survey, Work

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


def validate(survey: Survey, checks: list[LinkCheck]) -> None:
    works = survey["works"]
    if len(works) != 22 or len({w["id"] for w in works}) != 22:
        raise ValueError("The paper dataset must contain 22 uniquely identified works.")
    if {w["paper_reference"] for w in works} != set(range(8, 30)):
        raise ValueError("The paper records must cover references [8] through [29] exactly once.")
    records = works + survey["additional_works"]
    if len({w["id"] for w in records}) != len(records):
        raise ValueError("Core and additional records must have distinct identifiers.")
    for work in works:
        if work["year"] != int(work["bibliography"]["year"]):
            raise ValueError(f"Conflicting publication years for {work['name']}.")
        bib = work["bibliography"]
        source_url = (f"https://doi.org/{bib['doi']}" if bib["doi"] else
                      f"https://arxiv.org/abs/{bib['eprint']}" if bib["eprint"] else None)
        if source_url and work["publication_url"] != source_url:
            raise ValueError(f"The scholarly link does not match the identifier for {work['name']}.")
        if work["domain"] not in {*DOMAIN, "Mars", "Lunar", "Icy moon"}:
            raise ValueError(f"Unknown domain for {work['name']}.")
        category = work["category"]
        group = ("Construction" if category in ("Excavator", "Exc./Truck") else
                 category if category in ("Aerial", "Multi-platform") else
                 "Rover-relevant" if category in ("Rover", "Rover-relevant") else None)
        if group is None or work["platform_group"] != group:
            raise ValueError(f"Conflicting platform classification for {work['name']}.")
        if bool(work["resource_url"]) != (work["access_as_reported"] != "No release listed"):
            raise ValueError(f"Conflicting release link for {work['name']}.")
    if Counter(w["access_as_reported"] for w in works) != {"Direct": 12, "Request": 1, "No release listed": 9}:
        raise ValueError("Access counts must match the paper baseline.")
    if Counter(w["platform_group"] for w in works) != {"Rover-relevant": 16, "Construction": 3, "Aerial": 2, "Multi-platform": 1}:
        raise ValueError("Platform counts must match the paper baseline.")
    date.fromisoformat(survey["updated_on"])
    urls = {r[field] for r in records
            for field in ("publication_url", "resource_url") if r[field]}
    if {c["url"] for c in checks} != urls or len(checks) != len(urls):
        raise ValueError("Every listed external resource needs exactly one check record.")
    for check in checks:
        if check["status"] not in STATUS:
            raise ValueError("Unknown link-check status.")
        datetime.fromisoformat(check["checked_at"])
        if check["confirmed_reachable_on"] and check["status"] != "reachable":
            raise ValueError("An unsuccessful check cannot claim confirmed reachability.")
        if check["status"] == "reachable" and (check["http_status"] != 200 or
                check["confirmed_reachable_on"] != check["checked_at"][:10]):
            raise ValueError("A reachable result needs a successful response and matching date.")
        for url in (check["url"], check["final_url"]):
            if url:
                parsed = urlparse(url)
                if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                    raise ValueError("Only public HTTPS resource URLs are allowed.")


def result_label(check: LinkCheck) -> str:
    code = f" · HTTP {check['http_status']}" if check["http_status"] else ""
    return STATUS[check["status"]] + code


def resource(label: str, url: str | None, checks: dict[str, LinkCheck]) -> str:
    if not url:
        return f'<div class="resource-block"><h4>{esc(label)}</h4><p class="check-meta">No link recorded in the paper.</p></div>'
    check = checks[url]
    checked = check["checked_at"][:10]
    confirmed = check["confirmed_reachable_on"] or "Not confirmed in this check"
    return (f'<div class="resource-block"><h4>{esc(label)}</h4>'
            f'<a class="resource-url" href="{esc(url)}">{esc(url)}</a>'
            f'<p class="check-meta">Last checked: <time datetime="{esc(checked)}">{esc(checked)}</time> (UTC)'
            f'<br>{esc(result_label(check))}<br>Confirmed reachable: {esc(confirmed)}</p></div>')


def record(work: Work, checks: dict[str, LinkCheck]) -> str:
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


def related(work: RelatedWork, checks: dict[str, LinkCheck]) -> str:
    return (f'<article class="related-work" id="related-{esc(work["id"])}"><div><span class="badge">{esc(work["status"])}</span>'
            f'<h3>{esc(work["name"])}</h3><p class="related-year">{work["year"]}</p></div><div class="related-content">'
            f'<p class="record-title">{esc(work["title"])}</p><p>{esc(work["scope_note"])}</p><p>{esc(work["decision_note"])}</p>'
            f'<p class="historical-note">Original exclusion reason: {esc(work["historical_reason"] or "Not recorded in the available screening materials.")} '
            f'Companion note reviewed: {esc(work["reviewed_on"])}. Basis: {esc(work["basis"])}</p><div class="resource-grid">'
            + resource("Scholarly source", work["publication_url"], checks)
            + (resource("Repository", work["resource_url"], checks) if work["resource_url"] else "")
            + '</div></div></article>')


def main() -> None:
    survey = SURVEY
    validate(survey, CHECKS)
    checks = {c["url"]: c for c in CHECKS}
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
    print(f"Built index.html with 22 surveyed works and {len(checks)} visible link checks.")


if __name__ == "__main__":
    main()

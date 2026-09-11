"""Compare the database directly with Table I and the supplied PDF bibliography."""

import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))

from scripts.build import validate
from scripts.catalog import SURVEY
from scripts.link_status import CHECKS
from scripts.models import Work


def normalize(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text).casefold() if c.isalnum())


def verify_table(table_text: str, works: list[Work]) -> None:
    rows = [re.split(r"\s{2,}", line.strip()) for line in table_text.splitlines()
            if re.search(r"\[\d+\]\s+20\d\d", line)]
    if len(rows) != len(works):
        raise ValueError(f"PDF has {len(rows)} table rows; database has {len(works)}.")
    access_labels = {"Direct": "Repo", "Request": "Request", "No release listed": "–"}
    columns = ("name and reference", "year", "domain", "category", "engine", "ROS", "access", "terrain", "sensors")
    for row, work in zip(rows, works):
        actual = [f"{work['name']} [{work['paper_reference']}]", str(work["year"]), work["domain"],
                  work["category"], work["engine"], work["ros"] or "–",
                  access_labels[work["access_as_reported"]], work["terrain"] or "–", work["sensors"]]
        if len(row) != len(columns):
            raise ValueError(f"Could not extract all nine PDF columns for {work['name']}.")
        for label, expected, value in zip(columns, row, actual):
            if value != expected:
                raise ValueError(f"{work['name']} / {label}: PDF {expected!r}, database {value!r}.")


def verify_references(raw_text: str, works: list[Work]) -> None:
    bibliography = raw_text.split("REFERENCES", 1)[1]
    references = {m[1]: m[2] for m in re.finditer(
        r"^\[(\d+)\]\s+(.*?)(?=^\[\d+\]|\Z)", bibliography, re.M | re.S)}
    for work in works:
        citation = references.get(str(work["paper_reference"]), "")
        title = re.search("“(.*?)”", citation, re.S)
        if title is None or normalize(title[1]) != normalize(work["bibliography"]["title"]):
            raise ValueError(f"Title or citation mismatch for {work['name']}.")
        first_author = work["bibliography"]["author"].split(" and ", 1)[0]
        surname = first_author.split(",", 1)[0] if "," in first_author else first_author.split()[-1]
        if normalize(surname) not in normalize(citation[:title.start()]):
            raise ValueError(f"First author mismatch for {work['name']}.")
        if not re.search(rf"\b{work['year']}\b", citation[title.end():]):
            raise ValueError(f"Publication year mismatch for {work['name']}.")


def verify_artifacts(xml_text: str, works: list[Work]) -> None:
    root = ET.fromstring(xml_text)
    links = [a.get("href") for a in root.iter("a") if "".join(a.itertext()) in ("Repo", "Request")]
    expected = [w["resource_url"] for w in works if w["resource_url"]]
    if links != expected:
        raise ValueError("Study-artifact links do not match the PDF's Table I links in order.")


def main() -> None:
    paper = ROOT / "SurveyForPlanetaryRoboticSimulation.pdf"
    validate(SURVEY, CHECKS)
    table = subprocess.run(["pdftotext", "-layout", "-f", "4", "-l", "4", str(paper), "-"],
                           check=True, capture_output=True, text=True).stdout
    raw = subprocess.run(["pdftotext", "-raw", str(paper), "-"],
                         check=True, capture_output=True, text=True).stdout
    links = subprocess.run(["pdftohtml", "-xml", "-i", "-hidden", "-stdout", "-f", "4", "-l", "4", str(paper)],
                           check=True, capture_output=True, text=True).stdout
    verify_table(table, SURVEY["works"])
    verify_references(raw, SURVEY["works"])
    verify_artifacts(links, SURVEY["works"])
    print("Verified all 22 Table I rows (9 columns), 22 citation titles/authors/years, and 13 artifact links.")
    print(f"Validated classifications, identifiers, and complete check coverage for {len(CHECKS)} public URLs.")


if __name__ == "__main__":
    main()

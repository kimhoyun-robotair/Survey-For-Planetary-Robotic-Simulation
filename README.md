# Planetary Robotics Simulation — Survey Companion

English supporting materials for *Simulation for Planetary Robotic Perception and Autonomy: A Concise Survey of Recent Capabilities and Gaps*.

Project Page Address: https://kimhoyun-robotair.github.io/Survey-For-Planetary-Robotic-Simulation/

## Content and evidence

- The database reproduces all 22 works in Table I, including the paper's access and platform classifications.
- Each record includes the paper's reference number, a scholarly source when an identifier is recorded, the listed artifact URL, and current link-check results.
- SRB is documented as an additional related framework. Kamohara et al. and Kern et al. are identified by the paper as related work outside its core set. None changes the 22-work totals.
- Original search databases, exact queries, cutoff dates, and individual screening reasons are marked as unrecorded where the supplied materials do not establish them.
- A response check is not a reproduction test. Unconfirmed or restricted responses do not establish global unavailability.

## Files

| File | Purpose |
| --- | --- |
| `data/survey.json` | Curated source of truth: paper baseline and additional-work notes |
| `data/link-checks.json` | Dated response checks for publication and artifact URLs |
| `data/survey.csv` | Downloadable paper dataset, joined with current link-check results |
| `data/references.bib` | Bibliographic metadata for the 22 paper records |
| `templates/index.html` | English page content and static-page template |
| `scripts/build.py` | Validates baseline totals and generates HTML, CSV, and BibTeX |
| `scripts/check_links.py` | Refreshes the current link-check snapshot without changing paper classifications |
| `index.html`, `style.css`, `app.js` | Static site ready for hosting |

## Update and preview

Python 3.10 or newer is sufficient; the scripts use only the standard library.

```sh
python3 scripts/build.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Open the preview in a browser using port 8000. Search and filters progressively enhance the page; records and links remain readable without JavaScript.

To check links again, run the following before rebuilding:

```sh
python3 scripts/check_links.py
python3 scripts/build.py
```

This replaces the latest check snapshot. Preserve prior snapshots through version control when maintaining a history. Review responses before interpreting them: an HTTP 202 or an access restriction is not a confirmed resource page.

## Curation rules

Keep paper classifications fixed to the cited baseline. Record new literature in `additional_works`; explain present-day editorial treatment separately from any documented original decision. Do not invent a past search or exclusion history. A missing link is an explicit gap, not a placeholder URL.

The source PDF checksum identifies the paper used for transcription. The source document itself is not bundled. Public artifacts contain only selected bibliographic, survey, and resource-check fields; omit private contact details, local paths, host identifiers, request headers, and raw diagnostic output. The website uses no analytics, external fonts, or third-party scripts.

The build prepares local files. Publishing them is a separate repository operation.

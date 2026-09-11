# Planetary Robotics Simulation Survey

Project page and browsable database for **Simulation for Planetary Robotic Perception and Autonomy: A Concise Survey of Recent Capabilities and Gaps**, accepted at **iSpaRo 2026 — IEEE International Conference on Space Robotics**.

**Hoyun Kim and Giseop Kim**

Department of Robotics and Mechatronics Engineering, DGIST, Daegu, Republic of Korea.

Corresponding author: Giseop Kim.

[Project page](https://kimhoyun-robotair.github.io/Survey-For-Planetary-Robotic-Simulation/) · [Paper](SurveyForPlanetaryRoboticSimulation.pdf)

## Page content

- Full paper title, authors, affiliation, abstract, and a direct Paper link.
- Figure 5, extracted from page 6 of the supplied PDF with all seven explanation blocks intact. Its caption preserves the paper’s acknowledgement that the Mars scene was generated with ChatGPT Image 2.0.
- All 22 Table I works, with search, domain/platform/access filters, expandable profiles, scholarly sources, and study-artifact links.
- Three separate related-work notes and dated link responses. These additions do not change the paper’s comparison or counts.

The page is static HTML with progressive JavaScript enhancement. Records, disclosures, images, and paper links remain usable without JavaScript. It uses system fonts and no analytics or third-party scripts.

## Build and preview

Python 3.10 or newer is sufficient for the build; there are no third-party Python dependencies.

```sh
python3 scripts/build.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000`. Relative asset links also support the GitHub Pages project subdirectory.

To refresh public link responses:

```sh
python3 scripts/check_links.py
python3 scripts/build.py
```

To compare the database directly with the supplied paper:

```sh
python3 scripts/verify_catalog.py
```

The PDF comparison requires the installed Poppler utilities `pdftotext` and `pdftohtml`; the ordinary build and hosted page do not. It checks every Table I cell, citation title/first author/year, and listed artifact link. See [VERIFICATION.md](VERIFICATION.md) for the current review and its limits.

## Maintenance

| File | Purpose |
| --- | --- |
| `SurveyForPlanetaryRoboticSimulation.pdf` | Accepted paper opened by the Paper button |
| `assets/figure-5.png` | Complete Figure 5, rendered from the supplied PDF |
| `templates/index.html` | Page structure, abstract, captions, and explanatory text |
| `scripts/catalog.py` | Curated source records for the page builder |
| `scripts/link_status.py` | Latest dated resource responses |
| `scripts/models.py` | Record types shared by the maintenance scripts |
| `scripts/build.py` | Record validation and static HTML generation |
| `scripts/check_links.py` | Resource-response refresh |
| `scripts/verify_catalog.py` | Independent comparison with the supplied PDF |
| `index.html`, `style.css`, `app.js` | Website served directly by the host |

Edit the template or catalog and rebuild; do not hand-edit generated records in `index.html`. Keep the paper’s classifications fixed and place new literature in the additional-work list. Explain source supplements or disagreements in the relevant record. A response check does not establish installation success or reproducibility, and an unconfirmed response does not establish global unavailability.

The supplied paper and in-repository figure are sufficient for the website. Its build has no dependency on the separate paper-writing repository. Local generation does not publish the site.

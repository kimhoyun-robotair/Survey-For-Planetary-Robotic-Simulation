# Database and page verification

Reviewed on **2026-09-11** against the supplied `SurveyForPlanetaryRoboticSimulation.pdf`.

## Paper transcription

`python3 scripts/verify_catalog.py` independently extracts the supplied PDF and checks:

- All **22 rows × 9 columns** of Table I, including names/reference numbers, years, domains, categories, engines, middleware, release classifications, terrain sources, and sensors/outputs.
- All **22 reference titles, first-author surnames, and publication years** against the PDF bibliography. Typographic differences and PDF line wrapping are normalized for this comparison.
- All **13 study-artifact URLs**, in their Table I order, against the PDF’s embedded links.
- Unique identifiers and references, consistent platform groups, publication-link/identifier agreement, and exactly one dated response record per public URL.

All comparisons passed. The access distribution remains **12 direct / 1 request / 9 without a listed release**. The primary-platform distribution remains **16 rover-relevant / 3 construction / 2 aerial / 1 multi-platform**. The three additional works are excluded from these counts.

The complete displayed abstract also matches the PDF, including its final project-website sentence. The full paper title, both authors, shared DGIST affiliation, and corresponding-author attribution were checked against page 1.

Deliberately changed sensor fields, citation numbers, artifact URLs, platform groups, and reachability claims were rejected by the production validation/comparison functions. In particular, swapping platform groups while preserving their totals is detected.

## Publication-source review

The titles of all **17 DOI-indexed core works** were matched against each work’s Crossref registration record, with first-author surnames also checked. For example, the [Giubilato et al. registration](https://api.crossref.org/works/10.1109%2FMetroAeroSpace48742.2020.9160154) matches reference [23]. The remaining four existing preprint links were checked against their arXiv records: [Linde et al.](https://arxiv.org/abs/2505.22091), [Lindmark et al.](https://arxiv.org/abs/2509.12367), [PlanetaryPathBench](https://arxiv.org/abs/2512.21438), and [MARTIAN](https://arxiv.org/abs/2605.29647).

The final core work, Kurt et al., was found in the [official Space Robotics Workshop program](https://space-robotics-workshop.github.io/icra2026/) and matched to its [OpenReview paper](https://openreview.net/pdf?id=YdtCNcDCIV). All 22 core records now have a scholarly-source link. Its study-artifact classification remains “No release listed.”

The additional-work titles were checked against [SRB](https://arxiv.org/abs/2509.23328), [Kamohara et al.](https://arxiv.org/abs/2408.13468), and [Kern et al.](https://doi.org/10.1109/iSpaRo66239.2025.11436587). SRB’s planetary/orbital scope and the cited sections were checked in [its own paper](https://arxiv.org/html/2509.23328v1). The other two works remain outside the core dataset as stated in the survey’s Section III-E.

### Supplements and source disagreement

- **LunarRoverSim:** restored the missing conference name, *2024 9th International Conference on Automation, Control and Robotics Engineering (CACRE)*, using the [publisher’s registered metadata](https://api.crossref.org/works/10.1109%2FCACRE62362.2024.10634867). The record identifies this supplement.
- **Kurt et al.:** added the official scholarly-paper link. Its profile and access classification still reproduce Table I.
- **MarsSim:** retained **2023**, which is stated in both Table I and the survey bibliography. The [DOI registry](https://api.crossref.org/works/10.1109%2FTAES.2022.3207705) currently gives **2022**; the record explicitly documents this disagreement.

## Resource responses

All **39 distinct public URLs** were checked on 2026-09-11 (UTC):

| Recorded response | Count |
| --- | ---: |
| Reachable response with content | 21 |
| Response not sufficient to confirm reachability | 16 |
| Access restricted | 2 |
| Missing-page response or request failure | 0 |

The 16 unconfirmed responses returned HTTP 202; the two restricted responses returned HTTP 403. Bibliographic verification through a registry or indexed source does not turn a restricted publication-page response into a successful direct check. The page preserves this distinction and displays the dates and actual response results.

These checks verify transcription, source identification, and public resource responses. They do **not** establish simulator installation success, physical fidelity, complete asset availability, or experimental reproducibility. Original search queries, cutoff dates, and per-work screening decisions remain unspecified where the supplied paper does not document them.

## Figure and rendered page

Figure 5 was rendered directly from page 6 of the supplied PDF at 288 dpi, preserving the full scene and all seven explanation blocks. The resulting image is 2020 × 1334 pixels; its caption and the paper’s scene-generation acknowledgement are visible below it. The separate paper-writing repository was inspected read-only and is not a build dependency.

Actual Chrome/Playwright checks passed on the generated static page, served under a GitHub Pages-style project subdirectory:

- Direct Paper-button navigation to a valid PDF and full-resolution figure navigation.
- Local stylesheet, script, icon, image, and paper loading, with all section anchors resolving.
- Search, combined domain/platform/access filters, reset, empty results, and the expected access/platform totals.
- Native keyboard disclosure controls and the newly supplemented records.
- 320, 390, 768, and 1440 px layouts, open records, and an expanded verification table without page-level horizontal overflow.
- Reading all 22 records and opening native disclosures with JavaScript disabled.
- Reduced-motion behavior and no page runtime or console errors.

The opening layout, figure/caption, desktop/tablet database, and mobile expanded record were also visually inspected. Build generation, the PDF comparison, JavaScript syntax, Python type-error checks, and diff whitespace checks passed. No deployment was performed.

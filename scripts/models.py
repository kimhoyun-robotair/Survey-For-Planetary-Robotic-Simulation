from typing import Literal, TypedDict


class Bibliography(TypedDict):
    title: str
    author: str
    year: str
    doi: str | None
    eprint: str | None
    journal: str | None
    booktitle: str | None


class Paper(TypedDict):
    title: str
    source_locator: str
    work_count: int
    original_search_databases: None
    original_search_queries: None
    original_search_cutoff: None
    original_screening_log: None
    original_resource_check_dates: None


class Work(TypedDict):
    id: str
    name: str
    year: int
    domain: str
    category: str
    platform_group: str
    engine: str
    ros: str | None
    access_as_reported: str
    terrain: str | None
    sensors: str
    bibliography: Bibliography
    publication_url: str | None
    resource_url: str | None
    resource_type: str | None
    paper_reference: int
    evidence: str
    note: str


class RelatedWork(TypedDict):
    id: str
    name: str
    year: int
    title: str
    status: str
    publication_url: str | None
    resource_url: str | None
    basis: str
    scope_note: str
    decision_note: str
    historical_reason: str | None
    reviewed_on: str


class Survey(TypedDict):
    updated_on: str
    paper: Paper
    works: list[Work]
    additional_works: list[RelatedWork]


CheckStatus = Literal["reachable", "access_restricted", "response_unconfirmed", "not_found", "request_failed"]


class LinkCheck(TypedDict):
    url: str
    checked_at: str
    http_status: int | None
    final_url: str | None
    status: CheckStatus
    confirmed_reachable_on: str | None

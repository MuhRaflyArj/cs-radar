from pathlib import Path
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

Decision = Literal["include", "exclude", "review"]
Topic = Literal["rag", "agents", "reasoning", "evaluation"]


class Record(BaseModel):
    """Base model of the scope-audit that rejects fields that not declared by each record."""

    model_config = ConfigDict(extra="forbid")


class ControlExpectation(Record):
    """Expected inclusion decision and topic labels for a control paper."""

    decision: Literal["include", "exclude"]
    topics: list[Topic]


class Query(Record):
    """Named arXiv API query and its request parameters."""

    name: str
    params: dict[str, str | int]


class Paper(Record):
    """Validated metadata for one arXiv paper version."""

    arxiv_id: str = Field(pattern=r"^\d{4}\.\d{4,5}$")
    version: int = Field(gt=0)
    title: str = Field(min_length=1)
    abstract: str
    authors: list[str]
    categories: list[str]
    published: AwareDatetime
    updated: AwareDatetime
    url: str

    @model_validator(mode="after")
    def validate_dates(self) -> "Paper":
        if self.updated < self.published:
            raise ValueError("Update date precedes first submission")

        return self


class SourceRecord(Record):
    """Provenance and cache details for one fetched API response."""

    url: str
    method: Literal["GET", "POST"]
    params: dict[str, str | int]
    cache_path: Path
    fetched_at: AwareDatetime
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    cache_hit: bool


class ReviewRecord(Record):
    paper: Paper
    scope_version: str
    taxonomy_version: str
    requests: list[str]

    rule_decision: Decision
    rule_reason: str
    topic_hints: dict[Topic, list[str]]
    control_expectation: ControlExpectation | None

    manual_decision: Decision | None = None
    manual_topic_labels: list[Topic] | None = None
    manual_reason: str | None = None


class AuditIssue(Record):
    """Problem encountered while fetching, parsing, or reviewing audit data."""

    kind: Literal["request", "parse", "conflict", "interrupted"]
    request: str
    message: str


class AuditResult(Record):
    """Counts, status, provenance, and output paths for one audit run."""

    run_id: str
    scope_version: str
    taxonomy_version: str
    configuration_sha256: str
    cutoff: AwareDatetime
    finished_at: AwareDatetime
    elapsed_seconds: float

    status: Literal["partial", "awaiting_manual_review", "interrupted"]
    received_entries: int
    unique_papers: int
    duplicate_entries: int
    parsing_failures: int
    network_requests: int
    retries: int
    network_bytes: int

    missing_controls: list[str]
    issues: list[AuditIssue]
    sources: dict[str, SourceRecord]
    review_path: Path
    manifest_path: Path

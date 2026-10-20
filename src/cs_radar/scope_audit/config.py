from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml
from pydantic import AwareDatetime, Field, model_validator

from cs_radar.scope_audit.models import ControlExpectation, Record, Topic


class AuditConfig(Record):
    """Validated settings and date-window calculations for the scope audit."""

    project_root: Path
    scope_version: str
    taxonomy_version: str

    cutoff: AwareDatetime
    history_years: int = Field(gt=0)
    window_days: int = Field(gt=0)

    categories: list[str] = Field(min_length=1)
    keywords: list[str] = Field(min_length=1)
    topic_cues: dict[Topic, list[str]]
    controls: dict[str, ControlExpectation]

    samples_per_window: int = Field(ge=1, le=10)
    broad_probe_size: int = Field(ge=1, le=2)
    entry_limit: int = Field(ge=1, le=40)

    request_interval_seconds: float = Field(ge=3)
    request_timeout_seconds: float = Field(gt=0)
    max_http_requests: int = Field(ge=5, le=7)
    max_retries: int = Field(ge=0, le=2)
    max_retry_wait_seconds: float = Field(ge=3)
    response_limit_bytes: int = Field(gt=0)
    response_budget_bytes: int = Field(gt=0)
    user_agent: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_scope(self) -> "AuditConfig":
        self.cutoff = self.cutoff.astimezone(UTC)

        if self.history_years >= self.cutoff.year:
            raise ValueError("history_years must produce a valid calendar year")

        planned_entries = 3 * self.samples_per_window + self.broad_probe_size + len(self.controls)

        if planned_entries > self.entry_limit:
            raise ValueError("Request schedule exceeds entry_limit")

        if self.history_start >= self.previous_start:
            raise ValueError("History must extend before both comparison windows")

        if self.response_limit_bytes > self.response_budget_bytes:
            raise ValueError("Per-response limit exceeds total response budget")

        phrases = self.categories + self.keywords
        phrases += [cue for cues in self.topic_cues.values() for cue in cues]

        if any(not phrase.strip() for phrase in phrases):
            raise ValueError("Categories, keywords, and cues cannot be blank")

        return self

    @property
    def history_start(self) -> datetime:
        year = self.cutoff.year - self.history_years
        try:
            return self.cutoff.replace(year=year)
        except ValueError:
            return self.cutoff.replace(year=year, day=28)

    @property
    def recent_start(self) -> datetime:
        return self.cutoff - timedelta(days=self.window_days)

    @property
    def previous_start(self) -> datetime:
        return self.cutoff - timedelta(days=2 * self.window_days)


def load_config(path: Path) -> AuditConfig:
    path = path.resolve()

    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ValueError(f"Cannot read configuration: {path}") from error

    if not isinstance(document, dict):
        raise ValueError(f"Configuration root must be a mapping: {path}")

    section = document.get("scope_audit")
    if not isinstance(section, dict):
        raise ValueError(f"Missing or invalid scope_audit section: {path}")

    config = AuditConfig.model_validate(section)
    config.project_root = (path.parent / config.project_root).resolve()
    return config

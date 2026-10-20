import hashlib
import logging
import time
from datetime import UTC, datetime
from http.client import HTTPException
from pathlib import Path
from xml.etree import ElementTree as ET

from cs_radar.scope_audit.arxiv import ArxivClient, AtomParser
from cs_radar.scope_audit.config import AuditConfig
from cs_radar.scope_audit.models import (
    AuditIssue,
    AuditResult,
    ReviewRecord,
    SourceRecord,
)
from cs_radar.scope_audit.scope import QueryBuilder, ScopeReviewer


class AuditWriter:
    def __init__(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=False)
        self.review_path = directory / "review.jsonl"
        self.manifest_path = directory / "manifest.json"

    def write(self, records: list[ReviewRecord], result: AuditResult) -> None:
        with self.review_path.open("x", encoding="utf-8") as file:
            for record in records:
                file.write(record.model_dump_json() + "\n")

        with self.manifest_path.open("x", encoding="utf-8") as file:
            file.write(result.model_dump_json(indent=2))


class ScopeAudit:
    def __init__(
        self,
        config: AuditConfig,
        client: ArxivClient,
        parser: AtomParser,
        reviewer: ScopeReviewer,
        logger: logging.Logger,
    ) -> None:
        self.config = config
        self.client = client
        self.parser = parser
        self.reviewer = reviewer
        self.logger = logger

    def run(self, run_id: str) -> AuditResult:
        started = time.monotonic()
        writer = AuditWriter(directory=self.config.project_root / "outputs/scope-audit" / run_id)

        records: dict[str, ReviewRecord] = {}
        sources: dict[str, SourceRecord] = {}
        issues: list[AuditIssue] = []

        received, duplicates, parsing_failures = 0, 0, 0
        interrupted = False
        self.logger.info("audit_started", extra={"start_time": datetime.now()})

        try:
            for query in QueryBuilder(self.config).build():
                try:
                    body, source = self.client.fetch(query)
                    sources[query.name] = source
                    count, papers, parse_issues = self.parser.parse(body, query.name)

                    if received + count > self.config.entry_limit:
                        raise ValueError("Audit entry limit exceeded")

                    received += count
                    parsing_failures += len(parse_issues)
                    issues.extend(parse_issues)

                    for paper in papers:
                        existing = records.get(paper.arxiv_id)
                        if existing is None:
                            records[paper.arxiv_id] = self.reviewer.review(paper, query.name)
                            continue

                        duplicates += 1
                        existing.requests.append(query.name)
                        if paper != existing.paper:
                            issues.append(
                                AuditIssue(
                                    kind="conflict",
                                    request=query.name,
                                    message=(f"Conflicting metadata for {paper.arxiv_id}"),
                                )
                            )

                except (
                    OSError,
                    ValueError,
                    RuntimeError,
                    HTTPException,
                    ET.ParseError,
                ) as error:
                    issues.append(
                        AuditIssue(
                            kind="request",
                            request=query.name,
                            message=str(error),
                        )
                    )

                    self.logger.exception(
                        "request_failed",
                        extra={"details": {"request": query.name}},
                    )

        except KeyboardInterrupt:
            interrupted = True
            issues.append(
                AuditIssue(
                    kind="interrupted",
                    request="audit",
                    message="Interrupted by user",
                )
            )

        missing = sorted(set(self.config.controls) - records.keys())
        status = "interrupted" if interrupted else "partial" if issues or missing else "awaiting_manual_review"

        result = AuditResult(
            run_id=run_id,
            scope_version=self.config.scope_version,
            taxonomy_version=self.config.taxonomy_version,
            configuration_sha256=hashlib.sha256(self.config.model_dump_json().encode()).hexdigest(),
            cutoff=self.config.cutoff,
            finished_at=datetime.now(UTC),
            elapsed_seconds=time.monotonic() - started,
            status=status,
            received_entries=received,
            unique_papers=len(records),
            duplicate_entries=duplicates,
            parsing_failures=parsing_failures,
            network_requests=self.client.requests,
            retries=self.client.retries,
            network_bytes=self.client.bytes_received,
            missing_controls=missing,
            issues=issues,
            sources=sources,
            review_path=writer.review_path,
            manifest_path=writer.manifest_path,
        )

        writer.write([records[key] for key in sorted(records)], result)
        self.logger.info(
            "audit_finished",
            extra={
                "details": {
                    "status": result.status,
                    "unique_papers": result.unique_papers,
                    "parsing_failures": result.parsing_failures,
                }
            },
        )

        return result

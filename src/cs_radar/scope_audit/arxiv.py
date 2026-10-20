import hashlib
import logging
import re
import time
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from cs_radar.scope_audit.config import AuditConfig
from cs_radar.scope_audit.models import AuditIssue, Paper, Query, SourceRecord


class AtomParser:
    namespace = {"atom": "http://www.w3.org/2005/Atom"}

    @classmethod
    def entries(cls, body: bytes) -> list[ET.Element]:
        root = ET.fromstring(body)
        if root.tag != f"{{{cls.namespace['atom']}}}feed":
            raise ValueError("Response is not an Atom feed")

        entries = root.findall("atom:entry", cls.namespace)
        for entry in entries:
            identifier = entry.findtext("atom:id", "", cls.namespace)
            if "/api/errors" in identifier:
                message = entry.findtext("atom:summary", "", cls.namespace)
                raise ValueError(f"arXiv API error: {message}")

        return entries

    def parse(self, body: bytes, request_name: str) -> tuple[int, list[Paper], list[AuditIssue]]:
        entries = self.entries(body)
        papers, issues = [], []

        for entry in entries:
            try:
                papers.append(self._xml_to_paper(entry))
            except ValueError as error:
                issues.append(AuditIssue(kind="parse", request=request_name, message=str(error)))

        return len(entries), papers, issues

    def _xml_to_paper(self, entry: ET.Element) -> Paper:
        identifier = entry.findtext("atom:id", "", self.namespace)
        address = urlsplit(identifier)

        if address.hostname not in {"arxiv.org", "export.arxiv.org"}:
            raise ValueError(f"Unexpected paper URL: {identifier}")

        match = re.fullmatch(r"/abs/(\d{4}\.\d{4,5})v([1-9]\d*)", address.path)
        if not match:
            raise ValueError(f"Unexpected versioned paper ID: {identifier}")

        return Paper(
            arxiv_id=match[1],
            version=int(match[2]),
            title=" ".join(entry.findtext("atom:title", "", self.namespace).split()),
            abstract=" ".join(entry.findtext("atom:summary", "", self.namespace).split()),
            authors=[
                author.findtext("atom:name", "", self.namespace)
                for author in entry.findall("atom:author", self.namespace)
            ],
            categories=sorted(
                {
                    category.attrib["term"]
                    for category in entry.findall("atom:category", self.namespace)
                    if "term" in category.attrib
                }
            ),
            published=entry.findtext("atom:published", "", self.namespace),
            updated=entry.findtext("atom:updated", "", self.namespace),
            url=identifier,
        )


class ArxivClient:
    endpoint = "https://export.arxiv.org/api/query"

    def __init__(self, config: AuditConfig, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.cache_root = config.project_root / "data/sources/arxiv/metadata/cache"
        self.cache_root.mkdir(exist_ok=True, parents=True)

        self.requests = 0
        self.retries = 0
        self.bytes_received = 0
        self.last_request = 0.0

    def fetch(self, query: Query) -> tuple[bytes, SourceRecord]:
        """Return a validated cached or downloaded response with its provenance."""

        encoded_params = urlencode(sorted(query.params.items())).encode("utf-8")
        identity = b"POST\n" + self.endpoint.encode("utf-8") + b"\n" + encoded_params
        key = hashlib.sha256(identity).hexdigest()
        directory = self.cache_root / key
        body_path = directory / "response.xml"
        source_path = directory / "source.json"

        if directory.exists():
            if not body_path.is_file() or not source_path.is_file():
                raise RuntimeError(f"Incomplete cache, inspect {directory}")
            if body_path.stat().st_size > self.config.response_limit_bytes:
                raise ValueError(f"Cached response exceeds limit: {body_path}")

            body = body_path.read_bytes()
            source = SourceRecord.model_validate_json(source_path.read_text(encoding="utf-8"))

            if source.params != query.params or source.url != self.endpoint or source.method != "POST":
                raise ValueError(f"Cache request mismatch {directory}")

            if hashlib.sha256(body).hexdigest() != source.sha256:
                raise ValueError(f"Cache checksum mismatch: {body_path}")

            self._validate(body, query)
            self.logger.info("cache_hit", extra={"details": {"request": query.name}})

            return body, source.model_copy(update={"cache_hit": True, "cache_path": body_path})

        body = self._download(encoded_params)
        self._validate(body, query)

        source = SourceRecord(
            url=self.endpoint,
            method="POST",
            params=query.params,
            cache_path=body_path,
            fetched_at=datetime.now(UTC),
            sha256=hashlib.sha256(body).hexdigest(),
            cache_hit=False,
        )

        directory.mkdir()
        with body_path.open("xb") as file:
            file.write(body)
        with source_path.open("x", encoding="utf-8") as file:
            file.write(source.model_dump_json(indent=2))

        self.logger.info("response_cached", extra={"details": {"request": query.name}})

        return body, source

    @staticmethod
    def _validate(body: bytes, query: Query) -> None:
        entries = AtomParser.entries(body)
        if len(entries) > int(query.params["max_results"]):
            raise ValueError("Response exceeds the requested entry count")

    def _download(self, encoded_params: bytes) -> bytes:
        while True:
            if self.requests >= self.config.max_http_requests:
                raise RuntimeError("HTTP request budget exhausted")

            remaining = self.config.response_budget_bytes - self.bytes_received
            if remaining <= 0:
                raise RuntimeError("Response-byte budget exhausted")

            wait = self.config.request_interval_seconds - (time.monotonic() - self.last_request)
            time.sleep(max(0.0, wait))
            self.last_request = time.monotonic()
            self.requests += 1

            try:
                request = Request(
                    self.endpoint,
                    data=encoded_params,
                    headers={
                        "User-Agent": self.config.user_agent,
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    method="POST",
                )
                limit = min(self.config.response_limit_bytes, remaining)

                with urlopen(request, timeout=self.config.request_timeout_seconds) as response:
                    body = response.read(limit + 1)

                self.bytes_received += len(body)
                if len(body) > limit:
                    raise RuntimeError("Response exceeds byte limit")

                return body

            except HTTPError as error:
                status = error.code
                retry_after = error.headers.get("Retry-After")
                error.close()

                if status not in {429, 500, 502, 503, 504}:
                    raise

                self._retry(retry_after)

            except (URLError, TimeoutError, HTTPException):
                self._retry(None)

    def _retry(self, retry_after: str | None) -> None:
        if self.retries >= self.config.max_retries:
            raise RuntimeError("retry attempt exhausted")

        delay = self.config.request_interval_seconds * 2**self.retries
        if retry_after:
            try:
                server_delay = float(retry_after)
            except ValueError:
                retry_at = parsedate_to_datetime(retry_after)
                if retry_at.tzinfo is None:
                    retry_at = retry_at.replace(tzinfo=UTC)

                server_delay = (retry_at - datetime.now(UTC)).total_seconds()

            delay = max(delay, server_delay)

        if delay > self.config.max_retry_wait_seconds:
            raise RuntimeError("Server requested a longer deferral, retry later")

        self.retries += 1
        self.logger.warning("request_retry", extra={"details": {"delay_second": delay}})
        time.sleep(delay)

import re
import unicodedata
from datetime import datetime

from cs_radar.scope_audit.config import AuditConfig
from cs_radar.scope_audit.models import Paper, Query, ReviewRecord


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    text = re.sub(r"[-\u2010\u2011\u2012\u2013\u2014]", " ", text)
    return " ".join(text.split())


def contains(text: str, phrase: str) -> bool:
    pattern = rf"(?<!\w){re.escape(normalize(phrase))}(?!\w)"
    return re.search(pattern, text) is not None


class QueryBuilder:
    def __init__(self, config: AuditConfig) -> None:
        self.config = config

    def build(self) -> list[Query]:

        categories = " OR ".join(f"cat:{item}" for item in sorted(set(self.config.categories)))
        keywords = " OR ".join(f'(ti:"{term}" OR abs:"{term}")' for term in self.config.keywords)

        queries = []
        for name, start, end, order in (
            ("recent", self.config.recent_start, self.config.cutoff, "descending"),
            ("previous", self.config.previous_start, self.config.recent_start, "descending"),
            ("history", self.config.history_start, self.config.previous_start, "ascending"),
        ):
            expression = f"({categories}) AND ({keywords})"
            queries.append(self._search(name, expression, start, end, order))

        broad = f'({categories}) AND (ti:transformer OR ti:"multi-agent")'
        probe = self._search("broad_probe", broad, self.config.history_start, self.config.cutoff, "descending")
        probe.params["max_results"] = self.config.broad_probe_size

        queries.append(probe)
        queries.append(
            Query(
                name="controls",
                params={
                    "id_list": ",".join(self.config.controls),
                    "start": 0,
                    "max_results": len(self.config.controls),
                },
            )
        )

        return queries

    def _search(
        self,
        name: str,
        expression: str,
        start: datetime,
        end: datetime,
        order: str,
    ) -> Query:
        dates = f"submittedDate:[{start:%Y%m%d%H%M} TO {end:%Y%m%d%H%M}]"

        return Query(
            name=name,
            params={
                "search_query": f"{expression} AND {dates}",
                "start": 0,
                "max_results": self.config.samples_per_window,
                "sortBy": "submittedDate",
                "sortOrder": order,
            },
        )


class ScopeReviewer:
    def __init__(self, config: AuditConfig):
        self.config = config

    def review(self, paper: Paper, request_name: str) -> ReviewRecord:
        title = normalize(paper.title)
        text = normalize(f"{paper.title} {paper.abstract}")

        if not self.config.history_start <= paper.published < self.config.cutoff:
            decision, reason = "exclude", "out_of_window"
        elif not set(self.config.categories).intersection(paper.categories):
            decision, reason = "exclude", "category_outside_scope"
        elif paper.updated >= self.config.cutoff:
            decision, reason = "review", "post_cutoff_revision"
        elif not paper.abstract:
            decision, reason = "review", "insufficient_metadata"
        elif any(
            contains(title, term)
            for term in (
                "large language model",
                "large language models",
                "LLM",
                "LLMs",
            )
        ):
            decision, reason = "include", "llm_title_candidate"
        elif any(contains(text, term) for term in self.config.keywords):
            decision, reason = "review", "language_relevance_needs_review"
        else:
            decision, reason = "exclude", "no_language_indicator"

        hints = {topic: [cue for cue in cues if contains(text, cue)] for topic, cues in self.config.topic_cues.items()}

        return ReviewRecord(
            paper=paper,
            scope_version=self.config.scope_version,
            taxonomy_version=self.config.taxonomy_version,
            requests=[request_name],
            rule_decision=decision,
            rule_reason=reason,
            topic_hints=hints,
            control_expectation=self.config.controls.get(paper.arxiv_id),
        )

import hashlib
import logging
from datetime import UTC, datetime
from pathlib import Path

import yaml

from cs_radar.evaluation.models import EvaluationConfig, EvaluationManifest, QueryRecord
from cs_radar.scope_audit.config import AuditConfig


def load_config(path: Path) -> EvaluationConfig:
    """Resolve project_root relative to the configuration file."""

    path = path.resolve()

    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ValueError(f"Cannot read evaluation configuration: {path}") from error

    if not isinstance(document, dict):
        raise ValueError(f"Configuration root must be a mapping: {path}")

    section = document.get("prepare_evaluation")
    if not isinstance(section, dict):
        raise ValueError(f"Missing or invalid prepare_evaluation section: {path}")

    try:
        config = EvaluationConfig.model_validate(section)
    except ValueError as error:
        raise ValueError(f"Invalid prepare_evaluation section in {path}: {error}") from error

    config.project_root = (path.parent / config.project_root).resolve()
    return config


class EvaluationPreparer:
    """Publish the fixed queries, rubric, and completion manifest."""

    def __init__(
        self,
        config: EvaluationConfig,
        scope: AuditConfig,
        logger: logging.Logger,
    ) -> None:
        self.config = config
        self.scope = scope
        self.logger = logger

    def run(self, run_id: str) -> EvaluationManifest:
        self.logger.info("evaluation_prepare_started")

        queries = [
            QueryRecord(**query.model_dump(), cutoff=self.scope.cutoff)
            for query in sorted(self.config.queries, key=lambda query: query.query_id)
        ]

        query_bytes = "".join(query.model_dump_json() + "\n" for query in queries).encode("utf-8")
        rubric_bytes = (self.config.rubric.model_dump_json(indent=2) + "\n").encode("utf-8")

        artifacts = {
            "poc-queries.jsonl": query_bytes,
            "poc-rubric.json": rubric_bytes,
        }
        output_dir = self.config.project_root / self.config.output_dir

        result = EvaluationManifest(
            run_id=run_id,
            created_at=datetime.now(UTC),
            cutoff=self.scope.cutoff,
            history_start=self.scope.history_start,
            recent_start=self.scope.recent_start,
            previous_start=self.scope.previous_start,
            scope_version=self.scope.scope_version,
            taxonomy_version=self.scope.taxonomy_version,
            diagnostic_queries=sum(query.split == "diagnostic" for query in queries),
            holdout_queries=sum(query.split == "holdout" for query in queries),
            input_sha256={
                "evaluation_config": hashlib.sha256(self.config.model_dump_json().encode("utf-8")).hexdigest(),
                "scope_config": hashlib.sha256(self.scope.model_dump_json().encode("utf-8")).hexdigest(),
            },
            artifact_sha256={name: hashlib.sha256(content).hexdigest() for name, content in artifacts.items()},
            output_dir=output_dir,
        )

        output_dir.mkdir(parents=True, exist_ok=False)

        for name, content in artifacts.items():
            with (output_dir / name).open("xb") as file:
                file.write(content)

        # Publish the manifest last: its presence marks a completed bundle.
        with (output_dir / "manifest.json").open("x", encoding="utf-8") as file:
            file.write(result.model_dump_json(indent=2) + "\n")

        self.logger.info(
            "evaluation_prepare_finished",
            extra={
                "details": {
                    "diagnostic_queries": result.diagnostic_queries,
                    "holdout_queries": result.holdout_queries,
                    "output_dir": str(output_dir),
                }
            },
        )

        return result

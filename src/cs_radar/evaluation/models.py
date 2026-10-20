from pathlib import Path
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

Text = Annotated[str, Field(min_length=1)]
Workflow = Literal["growth", "timeline", "task", "unanswerable"]
Split = Literal["diagnostic", "holdout"]


class Record(BaseModel):
    """Reject unknown fields and normalize surrounding whitespace."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class QueryDefinition(Record):
    """One accepted evaluation question and its evidence requirements."""

    query_id: str = Field(pattern=r"^[GHTU]\d{2}$")
    workflow: Workflow
    split: Split
    question_template: Text
    required_behavior: Text
    required_evidence: list[Text] = Field(min_length=1)


class QueryRecord(QueryDefinition):
    """Persists a question with its frozen evaluation cutoff."""

    schema_version: Literal[1] = 1
    cutoff: AwareDatetime


class EvaluationRubric(Record):
    """Record the agreed targets without claiming an evaluation passed."""

    schema_version: Literal[1]
    usefulness_scale: dict[int, Text]
    minimum_useful_score: Literal[4]
    required_useful_responses: Literal[18]
    minimum_factual_accuracy: Literal[0.95]
    minimum_reviewed_claims: Literal[30]
    special_behaviors: dict[str, Literal["clarify", "abstain"]]
    review_rules: list[Text] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_contract(self) -> "EvaluationRubric":
        if set(self.usefulness_scale) != set(range(1, 6)):
            raise ValueError("The usefulness scale must contain scores 1 through 5")

        expected = {"T06": "clarify", "U01": "abstain", "U02": "abstain"}
        if self.special_behaviors != expected:
            raise ValueError(f"special_behaviors must equal {expected}")

        return self


class EvaluationConfig(Record):
    """Configure preparation of the fixed evaluation contract."""

    project_root: Path
    scope_config: Path
    output_dir: Path
    log_dir: Path
    rubric: EvaluationRubric
    queries: list[QueryDefinition] = Field(min_length=20, max_length=20)

    @model_validator(mode="after")
    def validate_queries(self) -> "EvaluationConfig":
        workflows = {
            "G": ("growth", 6),
            "H": ("timeline", 6),
            "T": ("task", 6),
            "U": ("unanswerable", 2),
        }

        expected_ids = {
            f"{prefix}{number:02d}" for prefix, (_, count) in workflows.items() for number in range(1, count + 1)
        }

        if {query.query_id for query in self.queries} != expected_ids:
            raise ValueError("Queries must contain each accepted G/H/T/U ID exactly once")

        for query in self.queries:
            prefix = query.query_id[0]
            number = int(query.query_id[1:])
            expected_workflow = workflows[prefix][0]
            expected_split = "diagnostic" if prefix != "U" and number <= 4 else "holdout"

            if query.workflow != expected_workflow or query.split != expected_split:
                raise ValueError(f"Incorrect workflow or split for {query.query_id}")

        for path in (self.scope_config, self.output_dir, self.log_dir):
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("Scope, output, and log paths must stay relative to project_root")

        return self


class EvaluationManifest(Record):
    """Describe prepared artifacts; it contains no answer-quality results."""

    schema_version: Literal[1] = 1
    run_id: str
    status: Literal["prepared"] = "prepared"
    created_at: AwareDatetime
    cutoff: AwareDatetime
    history_start: AwareDatetime
    recent_start: AwareDatetime
    previous_start: AwareDatetime
    scope_version: str
    taxonomy_version: str
    diagnostic_queries: int
    holdout_queries: int
    input_sha256: dict[str, str]
    artifact_sha256: dict[str, str]
    output_dir: Path

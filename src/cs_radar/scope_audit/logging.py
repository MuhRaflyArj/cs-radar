import json
import logging
from datetime import UTC, datetime
from pathlib import Path


class JsonFormatter(logging.Formatter):
    def __init__(self, run_id: str, stage: str = "scope_audit") -> None:
        super().__init__()
        self.run_id = run_id
        self.stage = stage

    def format(self, record: logging.LogRecord) -> str:
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "run_id": self.run_id,
            "stage": self.stage,
            "event": record.getMessage(),
            "details": getattr(record, "details", {}),
        }

        if record.exc_info:
            event["error"] = self.formatException(record.exc_info)

        return json.dumps(event, ensure_ascii=False, default=str)


def configure_logging(path: Path, run_id: str, stage: str = "scope_audit") -> logging.Logger:
    path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(f"cs_radar.{stage}.{run_id}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.FileHandler(path, mode="x", encoding="utf-8")
        handler.setFormatter(JsonFormatter(run_id, stage))
        logger.addHandler(handler)

    return logger

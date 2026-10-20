import argparse
import json
import logging
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

from cs_radar.evaluation import EvaluationPreparer
from cs_radar.evaluation.prepare import load_config
from cs_radar.scope_audit.config import load_config as load_scope_config
from cs_radar.scope_audit.logging import configure_logging


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    logger: logging.Logger | None = None

    try:
        config = load_config(args.config)
        scope = load_scope_config(config.project_root / config.scope_config)

        run_id = f"{datetime.now(UTC):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:8]}"
        log_path = config.project_root / config.log_dir / f"evaluation-prepare-{run_id}.jsonl"
        logger = configure_logging(log_path, run_id, stage="evaluation_prepare")

        result = EvaluationPreparer(config, scope, logger).run(run_id)

    except KeyboardInterrupt:
        if logger is not None:
            logger.warning("evaluation_prepare_interrupted")
        return 130

    except (OSError, ValueError) as error:
        if logger is not None:
            logger.exception("evaluation_prepare_failed")

        print(
            json.dumps(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "stage": "evaluation_prepare",
                    "event": "evaluation_prepare_failed",
                    "error": str(error),
                }
            ),
            file=sys.stderr,
        )

        return 1

    print(result.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

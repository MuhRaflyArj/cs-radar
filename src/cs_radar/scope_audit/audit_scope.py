import argparse
import json
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

from cs_radar.scope_audit import ScopeAudit
from cs_radar.scope_audit.arxiv import ArxivClient, AtomParser
from cs_radar.scope_audit.config import load_config
from cs_radar.scope_audit.logging import configure_logging
from cs_radar.scope_audit.scope import ScopeReviewer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    try:
        config = load_config(args.config)
        run_id = f"{datetime.now(UTC):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:8]}"
        logger = configure_logging(
            config.project_root / "logs" / f"scope-audit-{run_id}.jsonl",
            run_id,
        )

        pipeline = ScopeAudit(
            config=config,
            client=ArxivClient(config, logger),
            parser=AtomParser(),
            reviewer=ScopeReviewer(config),
            logger=logger,
        )
        result = pipeline.run(run_id)

    except KeyboardInterrupt:
        return 130
    except (OSError, ValueError, RuntimeError) as error:
        print(
            json.dumps({"event": "audit_failed", "error": str(error)}),
            file=sys.stderr,
        )
        return 1

    print(
        json.dumps(
            {
                "status": result.status,
                "manifest": str(result.manifest_path),
                "review": str(result.review_path),
            }
        )
    )

    if result.status == "interrupted":
        return 130
    return int(result.status == "partial")


if __name__ == "__main__":
    raise SystemExit(main())

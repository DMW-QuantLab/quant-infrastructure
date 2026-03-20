"""
Daily Monitor Report — called by monitor.yml at 08:00 UTC.
Checks Redis heartbeat, reads PnL state, generates HTML report.
"""
from __future__ import annotations
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import redis


def main() -> None:
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    r = redis.Redis.from_url(redis_url, decode_responses=True)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checks": {}
    }

    # Heartbeat check
    hb = r.get("rsa_bot:heartbeat")
    report["checks"]["bot_alive"] = hb is not None
    report["checks"]["last_heartbeat"] = hb

    # PnL state
    pnl_raw = r.get("rsa_bot:pnl_state")
    report["checks"]["pnl_state"] = json.loads(pnl_raw) if pnl_raw else None

    # Circuit breaker
    cb = r.get("rsa_bot:circuit_breaker")
    report["checks"]["circuit_breaker_open"] = cb == "1"

    # Write report
    out_dir = Path("reports")
    out_dir.mkdir(exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = out_dir / f"daily_{date_str}.json"
    out_path.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))

    # Fail CI if bot is not alive
    if not report["checks"]["bot_alive"]:
        print("ALERT: Bot heartbeat missing from Redis — bot may be down")
        sys.exit(1)


if __name__ == "__main__":
    main()


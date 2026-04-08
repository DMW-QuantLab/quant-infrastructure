# SKILLS: Quant Infrastructure Engineer
## Agent: quant-infrastructure-agent

---

## SKILL 1 — Risk Engine Maintenance

**Trigger:** Risk parameter change request from strategy-engines-agent OR human.

**Protocol:**
1. Parse the request: what parameter, what new value, what justification
2. Run impact analysis: which running bots does this affect?
3. Compute: given new parameter, what is the maximum theoretical drawdown across the current portfolio?
4. If breaking change (e.g., raising Kelly fraction, raising position cap): require human approval before merging
5. Update `src/risk/config.py` with the new parameter, increment MINOR version
6. Write tests that verify the new parameter behaves correctly at boundary conditions
7. PR to all consuming repos with version bump

**Core risk parameters (never change without human approval):**
```python
KELLY_FRACTION: float = 0.25          # Quarter-Kelly
MAX_POSITION_PCT: float = 0.05        # 5% of bankroll per market
MAX_CORRELATED_EXPOSURE: float = 0.20 # 20% across correlated cluster
DAILY_LOSS_CIRCUIT_BREAKER: float = 0.03  # -3% triggers pause
HARD_STOP_DRAWDOWN: float = 0.10      # -10% triggers full halt
MIN_TRADE_SIZE: float = 10.0          # $10 minimum
MAX_SPREAD_BPS: float = 6.0           # Skip markets above this
```

---

## SKILL 2 — Monitoring System

**Trigger:** Continuous — runs on schedule every 5 minutes.

**Protocol:**
1. Read all bot heartbeats from Redis (`heartbeat:<bot_id>`)
2. If any heartbeat stale > 2 minutes: open GitHub Issue `human-required` — "Bot <id> heartbeat missing"
3. Read current positions from Redis (`position:<bot_id>:<market_id>`)
4. Compute portfolio metrics:
   - Total notional exposure
   - Daily PnL (mark-to-market at current mid-price)
   - Rolling 30-day Sharpe per strategy
   - Max drawdown since inception per strategy
5. Check circuit breaker conditions (see README)
6. Write metrics to `monitoring/snapshots/<timestamp>.json`
7. Generate daily summary report at 08:00 UTC

**Metrics schema:**
```json
{
  "timestamp": "2024-11-10T08:00:00Z",
  "portfolio": {
    "total_notional": 4500.0,
    "daily_pnl": 127.50,
    "daily_pnl_pct": 0.0085,
    "drawdown_from_peak": -0.024,
    "circuit_breaker_active": false
  },
  "strategies": {
    "election_arb": {
      "sharpe_30d": 1.6,
      "positions": 3,
      "unrealised_pnl": 85.0
    }
  }
}
```

---

## SKILL 3 — Shared Library Development

**Trigger:** `infra-request` Issue from any agent.

**Protocol:**
1. Parse: what utility is needed, who needs it, what are the input/output types?
2. Design the interface before implementation (write the function signature and docstring first)
3. Implement with full type hints, no external dependencies unless absolutely necessary
4. Write unit tests achieving > 90% coverage
5. Document in `docs/api/<module>.md`
6. Bump PATCH version, update CHANGELOG
7. Open PRs to all repos that need the new version

**Core library modules:**
- `quant_infra.risk` — Kelly, sizing, circuit breaker, exposure checks
- `quant_infra.monitoring` — PnL tracker, Sharpe calculator, Brier Score
- `quant_infra.utils` — logging config, config loader, type definitions
- `quant_infra.auth` — environment variable loading patterns for secrets

---

## SKILL 4 — Deployment Configuration

**Trigger:** New bot ready for paper or live deployment.

**Protocol:**
1. Create `deploy/<bot_name>/` directory with:
   - `Dockerfile` — reproducible container build
   - `docker-compose.yml` — service definition with Redis dependency
   - `systemd/<bot_name>.service` — systemd unit file for process supervision
   - `config/env.template` — list of required environment variables (no values)
2. Verify: container starts, connects to Redis, emits heartbeat within 60 seconds
3. Document: startup sequence, shutdown sequence, log locations
4. Add bot to monitoring system config

**Dockerfile standard:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY config/ ./config/
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "src.bots.<bot_name>"]
```

---

## SKILL 5 — CI/CD Workflow Management

**Trigger:** New workflow needed OR existing workflow needs updating.

**Protocol:**
1. All workflow files live in `quant-infrastructure/.github/workflows/templates/`
2. Consuming repos pull templates via a setup script, not by copying manually
3. Standard workflows:
   - `ci.yml` — black, mypy, pytest, coverage (all repos)
   - `backtest.yml` — regression backtest on signal changes (strategy-engines only)
   - `experiment-log.yml` — auto-update registry on metrics.json changes (quant-research only)
   - `monitor.yml` — daily health report (quant-infrastructure)
4. Any workflow change: test in a feature branch first, verify on a non-main repo before propagating

---

## SKILL 6 — Secret Management Audit

**Trigger:** Scheduled weekly AND on any new repo setup.

**Protocol:**
1. Run `git log --all --full-history -- '**/*.env'` across all repos
2. Run `detect-secrets scan` on all repos
3. If secrets found: immediately alert human via Issue `human-required`, do not attempt cleanup without guidance
4. Verify all repos have `.gitignore` correctly excluding `.env`, `*.pem`, `*.key`
5. Verify GitHub Secrets are configured (do not read values, just check they exist)
6. Write audit report to `docs/security_audit_<date>.md`

---

## SKILL 7 — Correlation Matrix Maintenance

**Trigger:** New strategy added to portfolio OR weekly refresh.

**Protocol:**
1. Fetch historical PnL series for all active strategies from Redis
2. Compute pairwise return correlation matrix
3. Identify clusters of strategies with correlation > 0.6
4. Update `src/risk/correlation_matrix.json`
5. Alert strategy-engines-agent via Issue if any two strategies exceed 0.8 correlation (they may be duplicating the same trade)
6. Update portfolio-level Kelly sizing to account for correlation: `f_portfolio = f_single × (1 - max_cluster_correlation)`

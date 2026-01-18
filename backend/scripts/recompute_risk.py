from __future__ import annotations

from backend.config import get_settings
from backend.db import get_db
from backend.scripts.create_indexes import ensure_indexes
from backend.services.risk import compute_risk_scores
from backend.services.alerts import generate_alerts
from backend.services.forecasting import generate_forecasts


def run() -> None:
    # Touch config and DB to ensure connection is ready before work
    settings = get_settings()
    _ = get_db()
    print(f"Using database '{settings.db_name}'")

    ensure_indexes()

    risk_date, risk_docs = compute_risk_scores(target_date=None)
    alerts = generate_alerts(target_date=None)
    forecast_date, forecasts = generate_forecasts(target_date=None, horizon=7)

    print(f"risk computed: {len(risk_docs)} on date {risk_date or 'n/a'}")
    print(f"alerts generated: {len(alerts)}")
    print(f"forecasts generated: {len(forecasts)} on date {forecast_date or 'n/a'}")


def main() -> None:
    run()


if __name__ == "__main__":
    main()

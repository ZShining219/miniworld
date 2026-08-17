"""Run a disposable, read-only Lever integration proof with fictional location data."""

import json
import os
import tempfile
from pathlib import Path


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="miniworld-lever-") as temp_dir:
        database_path = Path(temp_dir) / "live-proof.db"
        os.environ.update(
            {
                "DATABASE_URL": f"sqlite:///{database_path}",
                "EXECUTION_MODE": "live",
                "SEED_DEMO_DATA": "false",
                "MODEL_PROVIDER_MODE": "demo",
                "ALLOW_LIVE_JOB_SEARCH": "true",
                "LIVE_JOB_SOURCE": "lever",
                "LEVER_SITES": "binance",
                "JOB_RESULTS_LIMIT": "3",
                "LANGGRAPH_CHECKPOINT_MODE": "memory",
                "SCHEDULER_ENABLED": "false",
            }
        )

        from fastapi.testclient import TestClient

        from app.main import app

        with TestClient(app) as client:
            fictional_exact_address = "公开验收用虚构香港位置"
            location = client.put(
                "/api/v1/location",
                json={
                    "exact_address": fictional_exact_address,
                    "latitude": 22.3193,
                    "longitude": 114.1694,
                    "is_demo": True,
                },
            )
            landmark = client.post(
                "/api/v1/landmarks",
                json={
                    "name": "公开验收地标",
                    "query_text": "Hong Kong",
                    "rotation_order": 0,
                    "enabled": True,
                },
            )
            run = client.post(
                "/api/v1/job-runs",
                json={"query": "internship", "live": True},
            )
            jobs = client.get("/api/v1/jobs")

        location.raise_for_status()
        landmark.raise_for_status()
        run.raise_for_status()
        jobs.raise_for_status()
        run_payload = run.json()
        job_payload = jobs.json()
        assert run_payload["status"] == "succeeded", run_payload
        assert run_payload["execution_mode"] == "live"
        assert run_payload["result_json"]["source"] == "lever"
        assert job_payload, "Lever returned no public postings for the proof landmark"
        assert all(item["source"].startswith("lever:") for item in job_payload)
        assert all(item["distance_status"] == "location_unresolved" for item in job_payload)
        assert all(item["distance_reason"] for item in job_payload)
        serialized = json.dumps(
            {"run": run_payload, "jobs": job_payload}, ensure_ascii=False
        )
        assert fictional_exact_address not in serialized
        assert "22.3193" not in serialized
        assert "114.1694" not in serialized
        print(
            json.dumps(
                {
                    "status": "passed",
                    "source": run_payload["result_json"]["source"],
                    "execution_mode": run_payload["execution_mode"],
                    "landmark": "Hong Kong",
                    "job_count": len(job_payload),
                    "distance_status": "location_unresolved",
                    "exact_location_exposed": False,
                    "external_write_performed": False,
                },
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()

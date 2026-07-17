"""Export the ML training dataset (features + completion label) to CSV + JSONL.

    python -m scripts.export_training_data           # -> training_data.csv / .jsonl
    python -m scripts.export_training_data out/foo    # custom prefix
"""
from __future__ import annotations

import asyncio
import csv
import json
import sys

from app.database.session import AsyncSessionLocal
from app.services.training_data_service import export_completion_dataset


async def main(prefix: str) -> None:
    async with AsyncSessionLocal() as db:
        rows = await export_completion_dataset(db)

    if not rows:
        print("No gameplay yet — nothing to export.")
        return

    fields = list(rows[0].keys())
    with open(f"{prefix}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with open(f"{prefix}.jsonl", "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Exported {len(rows)} rows -> {prefix}.csv / {prefix}.jsonl")


if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else "training_data"
    asyncio.run(main(prefix))

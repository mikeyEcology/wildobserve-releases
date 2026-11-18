"""Writes today's downloads of the newest release's files into downloads.csv.

GitHub keeps only a running total for each file, so a day's downloads are its
total at the day's last run minus the day before's. The workflow runs this
hourly, and each run rewrites today's rows. Days run midnight to midnight,
New York time. A release's first row holds everything since it came out.

Usage: record_downloads.py RELEASE.json downloads.csv
"""

import csv
import datetime
import json
import sys
import zoneinfo
from pathlib import Path

FIELDS = ["date", "tag", "asset", "downloads", "total"]

release = json.loads(Path(sys.argv[1]).read_text())
table = Path(sys.argv[2])
today = datetime.datetime.now(zoneinfo.ZoneInfo("America/New_York")).date().isoformat()
tag = release["tag_name"]

rows = list(csv.DictReader(table.open())) if table.exists() else []
rows = [r for r in rows if not (r["date"] == today and r["tag"] == tag)]
for asset in release["assets"]:
    earlier = [r for r in rows if r["tag"] == tag and r["asset"] == asset["name"]]
    before = int(earlier[-1]["total"]) if earlier else 0
    total = asset["download_count"]
    rows.append(
        {"date": today, "tag": tag, "asset": asset["name"], "downloads": total - before, "total": total}
    )

with table.open("w", newline="") as f:
    writer = csv.DictWriter(f, FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

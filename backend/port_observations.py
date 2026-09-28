"""Best-effort reader for the official Paradip Port Authority daily report."""

from __future__ import annotations

import json
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pdfplumber
import requests
from bs4 import BeautifulSoup


TRAFFIC_PAGE = "https://paradipport.gov.in/traffic/"
SNAPSHOT_CACHE = Path(__file__).resolve().parent / "ml_assets" / "data" / "paradip_snapshot.json"
REQUEST_HEADERS = {"User-Agent": "CargoPilot-prototype/1.0 (official public report reader)"}
DRY_BULK_CARGO = re.compile(
    r"THERMAL\s*COAL|TH\.\s*COAL|C\.\s*COAL|COAL|LIMESTONE|PHOSPH|FERTILI[ZS]ER|"
    r"IRON\s*ORE|ORE\s*PELLET|CLINKER|GYPSUM|BAUXITE|SULPHUR|CEMENT",
    re.IGNORECASE,
)


def _fetch_paradip_snapshot() -> dict:
    """Fetch the latest published traffic PDF and summarize its dry-bulk anchorage queue."""
    page = requests.get(TRAFFIC_PAGE, headers=REQUEST_HEADERS, timeout=12)
    page.raise_for_status()
    soup = BeautifulSoup(page.text, "html.parser")
    report_link = None
    report_label = None
    for link in soup.find_all("a", href=True):
        row = link.find_parent("tr")
        label = " ".join((row or link).get_text(" ", strip=True).split())
        if "Daily Traffic Report" in label and link["href"].lower().endswith(".pdf"):
            report_link = link["href"]
            report_label = label
            break
    if not report_link:
        raise ValueError("The port authority page did not list a daily traffic report.")

    if report_link.startswith("/"):
        report_link = "https://paradipport.gov.in" + report_link
    elif report_link.startswith("http://"):
        report_link = "https://" + report_link[len("http://"):]
    pdf_response = requests.get(report_link, headers=REQUEST_HEADERS, timeout=20)
    pdf_response.raise_for_status()

    with pdfplumber.open(BytesIO(pdf_response.content)) as pdf:
        pages = [page.extract_text(layout=False) or "" for page in pdf.pages]
    text = "\n".join(pages)
    upper = text.upper()
    start = upper.find("VESSELS WAITING AT ANCHORAGE")
    if start < 0:
        raise ValueError("The current traffic report has no readable anchorage section.")
    section = text[start:]
    for terminator in ("FOR OJ", "C. VESSELS", "C. SCHEDULE", "D. BERTHING MOVEMENTS"):
        position = section.upper().find(terminator)
        if position > 0:
            section = section[:position]

    rows = []
    for line in section.splitlines():
        normalized = " ".join(line.split())
        if re.match(r"^\d+\s+(?:MV|MT)\.", normalized, re.IGNORECASE):
            if DRY_BULK_CARGO.search(normalized):
                rows.append(normalized)

    if not rows:
        raise ValueError("Could not parse dry-bulk vessel rows from the anchorage section.")

    # Report headers include the authority's observation date and time.
    as_of = None
    date_match = re.search(r"AS ON\s+(\d{2}-\d{2}-\d{4})\s+AT\s+(\d{4})\s*HRS", text, re.I)
    if date_match:
        report_date = datetime.strptime(date_match.group(1), "%d-%m-%Y").date().isoformat()
        as_of = report_date + "T" + date_match.group(2)[:2] + ":" + date_match.group(2)[2:] + ":00"

    snapshot = {
        "status": "observed_snapshot",
        "is_stale": False,
        "port": "Paradip",
        "source": "Paradip Port Authority daily traffic report",
        "source_url": report_link,
        "report_label": report_label,
        "as_of": as_of,
        "dry_bulk_vessels_waiting_at_anchorage": len(rows),
        "cargo_types_observed": sorted({
            match.group(0).upper()
            for row in rows
            for match in re.finditer(r"THERMAL\s*COAL|TH\.\s*COAL|C\.\s*COAL|COAL|LIMESTONE|PHOSPH|FERTILI[ZS]ER|IRON\s*ORE|ORE\s*PELLET|CLINKER|GYPSUM|BAUXITE|SULPHUR|CEMENT", row, re.I)
        }),
        "interpretation": "Observed queue count; not AIS tracks, waiting-time prediction, or demurrage risk.",
    }
    SNAPSHOT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_CACHE.write_text(json.dumps(snapshot, indent=2) + "\n")
    return snapshot


def get_paradip_snapshot() -> dict:
    """Use the official daily report, falling back to its dated local cache if offline."""
    try:
        return _fetch_paradip_snapshot()
    except Exception:
        if not SNAPSHOT_CACHE.exists():
            raise
        snapshot = json.loads(SNAPSHOT_CACHE.read_text())
        snapshot["status"] = "cached_snapshot"
        snapshot["is_stale"] = True
        snapshot["interpretation"] = (
            "Cached official observation; verify the report date because the live source was unavailable. "
            "Not AIS tracking, waiting-time prediction, or demurrage risk."
        )
        return snapshot

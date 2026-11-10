"""Write an automated test result into test-execution-report.xlsx.

Example:
    python update_report.py --ts TS-001 --tc TC-001 --status Pass \
        --actual "Redirected to dashboard after login" \
        --location "http://localhost:5173/#/login -> http://localhost:5173/#/dashboard"
"""
import argparse
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

REPORT = Path(__file__).with_name("test-execution-report.xlsx")
SHEET = "Test Execution Result"
HEADER_ROW = 5
LOGIN_URL = "http://localhost:5173/#/login"
DASHBOARD_URL = "http://localhost:5173/#/dashboard"


def update_report(ts, tc, actual, status, location, executed_by="Automation", path=REPORT):
    wb = load_workbook(path)
    ws = wb[SHEET]
    cols = {str(c.value).strip(): c.column for c in ws[HEADER_ROW] if c.value}
    col = lambda prefix: next(i for name, i in cols.items() if name.startswith(prefix))

    for row in range(HEADER_ROW + 1, ws.max_row + 1):
        if ws.cell(row, col("Test Scenario ID")).value == ts and ws.cell(row, col("Test Case ID")).value == tc:
            ws.cell(row, col("Actual Result")).value = actual
            ws.cell(row, col("Status")).value = status
            ws.cell(row, col("Executed by")).value = executed_by
            ws.cell(row, col("Location")).value = location
            ws.cell(row, col("Executed Date")).value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                wb.save(path)
            except PermissionError:
                raise SystemExit(f"Cannot save {path}: close it in Excel and run again.")
            return row
    raise ValueError(f"{ts}/{tc} not found in '{SHEET}'")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ts", default="TS-001")
    p.add_argument("--tc", default="TC-001")
    p.add_argument("--status", default="Pass", choices=["Pass", "Fail", "Blocked"])
    p.add_argument("--actual", default="User logged in successfully and was redirected to the dashboard.")
    p.add_argument("--location", default=f"{LOGIN_URL} -> {DASHBOARD_URL}")
    p.add_argument("--executed-by", default="Automation")
    a = p.parse_args()
    print(f"Updated row {update_report(a.ts, a.tc, a.actual, a.status, a.location, a.executed_by)}")

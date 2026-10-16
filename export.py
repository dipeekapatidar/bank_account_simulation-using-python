"""Export a transaction history as CSV (for Excel) or TXT (printable statement)."""
import csv
import os
from datetime import datetime
from config import EXPORT_DIR, BANK_NAME, CURRENCY


def _filename(acc, ext):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(EXPORT_DIR, exist_ok=True)
    return os.path.join(EXPORT_DIR, f"{acc['account_no']}_history_{stamp}.{ext}")


def export_csv(acc):
    path = _filename(acc, "csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Date & Time", "Type", "Amount", "Balance After", "Note"])
        for t in acc["transactions"]:
            w.writerow([t["time"], t["type"], t["amount"], t["balance_after"], t["note"]])
    return path


def export_txt(acc):
    path = _filename(acc, "txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{BANK_NAME} - ACCOUNT STATEMENT\n{'=' * 70}\n")
        f.write(f"Name: {acc['name']}   Account: {acc['account_no']}   Type: {acc['type']}\n")
        f.write(f"Current balance: {CURRENCY} {acc['balance']:.2f}\n{'-' * 70}\n")
        f.write(f"{'Date & Time':<20}{'Type':<14}{'Amount':>10}{'Balance':>12}  Note\n")
        for t in acc["transactions"]:
            f.write(f"{t['time']:<20}{t['type']:<14}{t['amount']:>10.2f}{t['balance_after']:>12.2f}  {t['note']}\n")
    return path

"""Core banking logic: accounts, PIN security, transactions, interest, transfers."""
import hashlib
import secrets
from datetime import datetime, timedelta
import storage
from config import (BANK_CODE, ACCOUNT_TYPES, MAX_PIN_ATTEMPTS, LOCK_MINUTES)

TIME_FMT = "%Y-%m-%d %H:%M:%S"


def _now():
    return datetime.now().strftime(TIME_FMT)


def hash_pin(pin, salt_hex):
    """PINs are never stored as plain text - only a salted hash."""
    return hashlib.pbkdf2_hmac("sha256", pin.encode(), bytes.fromhex(salt_hex), 100_000).hex()


def valid_pin(pin):
    return pin.isdigit() and len(pin) == 4


class Bank:
    def __init__(self):
        self.accounts = storage.load_accounts()

    def _save(self):
        storage.save_accounts(self.accounts)

    def _log(self, acc, kind, amount, note=""):
        acc["transactions"].append({
            "time": _now(), "type": kind, "amount": round(amount, 2),
            "balance_after": round(acc["balance"], 2), "note": note})

    def get(self, acc_no):
        return self.accounts.get(acc_no.strip().upper())

    def type_info(self, acc):
        return next(t for t in ACCOUNT_TYPES.values() if t["name"] == acc["type"])

    # ---------- create & login ----------
    def create_account(self, name, type_key, pin, opening):
        if type_key not in ACCOUNT_TYPES:
            return False, "Invalid account type.", None
        if not name.strip():
            return False, "Name is required.", None
        if not valid_pin(pin):
            return False, "PIN must be exactly 4 digits.", None
        info = ACCOUNT_TYPES[type_key]
        if opening < info["min_balance"]:
            return False, f"Minimum opening balance is {info['min_balance']}.", None

        acc_no = f"{BANK_CODE}{100001 + len(self.accounts)}"
        salt = secrets.token_hex(16)
        acc = {"account_no": acc_no, "name": name.strip().title(), "type": info["name"],
               "balance": 0.0, "salt": salt, "pin_hash": hash_pin(pin, salt),
               "failed_attempts": 0, "locked_until": None,
               "opened_on": _now(), "transactions": []}
        acc["balance"] = round(opening, 2)
        self._log(acc, "OPENING", opening, "Account opened")
        self.accounts[acc_no] = acc
        self._save()
        return True, f"Account created. Your account number is {acc_no}", acc

    def login(self, acc_no, pin):
        acc = self.get(acc_no)
        if not acc:
            return False, "Account not found.", None
        if acc["locked_until"]:
            until = datetime.strptime(acc["locked_until"], TIME_FMT)
            if datetime.now() < until:
                mins = int((until - datetime.now()).total_seconds() // 60) + 1
                return False, f"Account is locked. Try again in about {mins} minute(s).", None
            acc["locked_until"], acc["failed_attempts"] = None, 0

        if secrets.compare_digest(hash_pin(pin, acc["salt"]), acc["pin_hash"]):
            acc["failed_attempts"] = 0
            self._save()
            return True, f"Welcome, {acc['name']}!", acc

        acc["failed_attempts"] += 1
        left = MAX_PIN_ATTEMPTS - acc["failed_attempts"]
        if left <= 0:
            acc["locked_until"] = (datetime.now() + timedelta(minutes=LOCK_MINUTES)).strftime(TIME_FMT)
            msg = f"Too many wrong attempts. Account locked for {LOCK_MINUTES} minutes."
        else:
            msg = f"Wrong PIN. {left} attempt(s) left."
        self._save()
        return False, msg, None

    def verify_pin(self, acc, pin):
        return secrets.compare_digest(hash_pin(pin, acc["salt"]), acc["pin_hash"])

    def change_pin(self, acc, old_pin, new_pin):
        if not self.verify_pin(acc, old_pin):
            return False, "Old PIN is incorrect."
        if not valid_pin(new_pin):
            return False, "New PIN must be exactly 4 digits."
        acc["salt"] = secrets.token_hex(16)
        acc["pin_hash"] = hash_pin(new_pin, acc["salt"])
        self._save()
        return True, "PIN changed successfully."

    # ---------- money operations ----------
    def deposit(self, acc, amount):
        if amount <= 0:
            return False, "Amount must be greater than zero."
        acc["balance"] = round(acc["balance"] + amount, 2)
        self._log(acc, "DEPOSIT", amount, "Cash deposit")
        self._save()
        return True, f"Deposited. New balance: {acc['balance']:.2f}"

    def _can_debit(self, acc, amount):
        info = self.type_info(acc)
        if amount <= 0:
            return False, "Amount must be greater than zero."
        if not info["can_withdraw"]:
            return False, f"{acc['type']} accounts do not allow withdrawals or transfers."
        if acc["balance"] - amount < info["min_balance"]:
            return False, f"Not allowed. Minimum balance of {info['min_balance']} must remain."
        return True, ""

    def withdraw(self, acc, amount):
        ok, msg = self._can_debit(acc, amount)
        if not ok:
            return False, msg
        acc["balance"] = round(acc["balance"] - amount, 2)
        self._log(acc, "WITHDRAW", amount, "Cash withdrawal")
        self._save()
        return True, f"Withdrawn. New balance: {acc['balance']:.2f}"

    def transfer(self, acc, to_no, amount):
        target = self.get(to_no)
        if not target:
            return False, "Receiver account not found."
        if target["account_no"] == acc["account_no"]:
            return False, "You cannot transfer to your own account."
        ok, msg = self._can_debit(acc, amount)
        if not ok:
            return False, msg
        acc["balance"] = round(acc["balance"] - amount, 2)
        target["balance"] = round(target["balance"] + amount, 2)
        self._log(acc, "TRANSFER OUT", amount, f"To {target['account_no']} ({target['name']})")
        self._log(target, "TRANSFER IN", amount, f"From {acc['account_no']} ({acc['name']})")
        self._save()
        return True, f"Transferred {amount:.2f} to {target['name']}. New balance: {acc['balance']:.2f}"

    # ---------- interest ----------
    def interest_for(self, acc, months):
        rate = self.type_info(acc)["rate"]
        return round(acc["balance"] * rate / 100 * months / 12, 2)

    def apply_interest(self, acc, months):
        if months <= 0:
            return False, "Months must be greater than zero."
        interest = self.interest_for(acc, months)
        if interest <= 0:
            return False, f"{acc['type']} accounts do not earn interest."
        acc["balance"] = round(acc["balance"] + interest, 2)
        self._log(acc, "INTEREST", interest, f"Interest for {months} month(s)")
        self._save()
        return True, f"Interest of {interest:.2f} added. New balance: {acc['balance']:.2f}"

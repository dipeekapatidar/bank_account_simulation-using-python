"""Settings for the Bank Account Simulation.
Change these values to customize the project as your own."""
import os

BANK_NAME = "My Simple Bank"        # <- change to your own bank name
CREATED_BY = "Your Name"            # <- put your name here
BANK_CODE = "MSB"                   # prefix of account numbers, e.g. MSB100001
CURRENCY = "Rs."

MAX_PIN_ATTEMPTS = 3                # wrong PIN tries before temporary lock
LOCK_MINUTES = 2                    # how long the account stays locked

# Account types: interest rate (% per year), minimum balance, withdrawals allowed?
ACCOUNT_TYPES = {
    "1": {"name": "Savings", "rate": 4.0, "min_balance": 500, "can_withdraw": True},
    "2": {"name": "Current", "rate": 0.0, "min_balance": 0, "can_withdraw": True},
    "3": {"name": "Fixed Deposit", "rate": 7.0, "min_balance": 1000, "can_withdraw": False},
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "accounts.json")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

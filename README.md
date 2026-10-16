# Bank Account Simulation (Python)

A simple command-line bank project. No external libraries needed, only Python 3.8+.

## Run
    python main.py        (Windows)
    python3 main.py       (Mac / Linux)

## Features
- Multiple account types: Savings, Current, Fixed Deposit
- Transaction history with date and time
- Interest calculation (rate depends on account type)
- Secure PIN login (PIN stored as a salted hash, hidden while typing)
- Account locks for a few minutes after 3 wrong PIN attempts
- Fund transfer between accounts (needs PIN confirmation)
- Export history as CSV (Excel) or TXT statement

## Files
| File | Purpose |
|------|---------|
| main.py | Menus and user interface |
| bank.py | Core logic (accounts, PIN, deposit, withdraw, transfer, interest) |
| storage.py | Reads/writes data/accounts.json |
| export.py | CSV and TXT export |
| config.py | Bank name, interest rates, account types |
| data/ | Saved accounts (created automatically) |
| exports/ | Exported statements (created automatically) |

## Customize
Open `config.py` and change `BANK_NAME`, `CREATED_BY`, `BANK_CODE`, interest rates and minimum balances.
You can also add a new account type by adding one more line in `ACCOUNT_TYPES`.

## Try it
Create two accounts, deposit money, transfer from one to the other, add interest,
then export the history from the menu.

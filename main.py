"""Bank Account Simulation - command line menu.
Run with:  python main.py
"""
import getpass
from bank import Bank
import export
from config import BANK_NAME, CREATED_BY, CURRENCY, ACCOUNT_TYPES

bank = Bank()


def banner():
    print("\n" + "=" * 56)
    print(f"  {BANK_NAME.upper()}")
    print(f"  Bank Account Simulation  |  by {CREATED_BY}")
    print("=" * 56)


def read_pin(prompt="  Enter 4-digit PIN: "):
    return input(prompt)
def read_amount(prompt):
    try:
        return float(input(prompt))
    except ValueError:
        print("  Please enter a valid number.")
        return 0


def show_history(acc, limit=None):
    rows = acc["transactions"][-limit:] if limit else acc["transactions"]
    print(f"\n  {'Date & Time':<20}{'Type':<14}{'Amount':>10}{'Balance':>12}  Note")
    print("  " + "-" * 78)
    for t in rows:
        print(f"  {t['time']:<20}{t['type']:<14}{t['amount']:>10.2f}{t['balance_after']:>12.2f}  {t['note']}")


# ---------- before login ----------
def create_account():
    name = input("  Full name: ")
    print("  Account types:")
    for k, t in ACCOUNT_TYPES.items():
        print(f"   {k}. {t['name']:<14} interest {t['rate']}% | min balance {t['min_balance']}")
    type_key = input("  Choose type: ").strip()
    opening = read_amount("  Opening deposit: ")
    pin = read_pin("  Set a 4-digit PIN: ")
    if pin != read_pin("  Confirm PIN: "):
        print("  PINs do not match.")
        return
    ok, msg, _ = bank.create_account(name, type_key, pin, opening)
    print("  " + msg)


def login():
    acc_no = input("  Account number: ")
    ok, msg, acc = bank.login(acc_no, read_pin())
    print("  " + msg)
    if ok:
        account_menu(acc)


# ---------- after login ----------
def account_menu(acc):
    while True:
        print(f"\n  {acc['name']} | {acc['account_no']} | {acc['type']}")
        print("   1. Check balance      5. Transaction history")
        print("   2. Deposit            6. Interest")
        print("   3. Withdraw           7. Export history")
        print("   4. Transfer           8. Change PIN")
        print("   0. Logout")
        c = input("\n  Your choice: ").strip()
        if c == "1":
            print(f"  Balance: {CURRENCY} {acc['balance']:.2f}")
        elif c == "2":
            print("  " + bank.deposit(acc, read_amount("  Amount: "))[1])
        elif c == "3":
            print("  " + bank.withdraw(acc, read_amount("  Amount: "))[1])
        elif c == "4":
            to = input("  Receiver account number: ")
            amt = read_amount("  Amount: ")
            if not bank.verify_pin(acc, read_pin("  Confirm with your PIN: ")):
                print("  Wrong PIN. Transfer cancelled.")
            else:
                print("  " + bank.transfer(acc, to, amt)[1])
        elif c == "5":
            show_history(acc)
        elif c == "6":
            try:
                months = int(input("  Number of months [1]: ") or 1)
            except ValueError:
                print("  Please enter a whole number.")
                continue
            print(f"  Expected interest: {CURRENCY} {bank.interest_for(acc, months):.2f}")
            if input("  Add it to your account? (y/n): ").lower() == "y":
                print("  " + bank.apply_interest(acc, months)[1])
        elif c == "7":
            kind = input("  Format - 1. CSV (Excel)  2. TXT statement: ").strip()
            path = export.export_csv(acc) if kind == "1" else export.export_txt(acc)
            print("  Saved to:", path)
        elif c == "8":
            ok, msg = bank.change_pin(acc, read_pin("  Old PIN: "), read_pin("  New PIN: "))
            print("  " + msg)
        elif c == "0":
            print("  Logged out.")
            return
        else:
            print("  Invalid choice.")


def main():
    banner()
    while True:
        print("\n  MAIN MENU\n   1. Create account\n   2. Login\n   0. Exit")
        c = input("\n  Your choice: ").strip()
        if c == "1":
            create_account()
        elif c == "2":
            login()
        elif c == "0":
            print(f"  Thank you for banking with {BANK_NAME}. Goodbye!")
            break
        else:
            print("  Invalid choice.")


if __name__ == "__main__":
    main()

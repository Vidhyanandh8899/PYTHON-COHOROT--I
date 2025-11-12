#!/usr/bin/env python3
"""
bank_system_with_pin_fixed_create.py
- Same as previous PIN-enabled banking system, but the interactive
  account creation flow now re-prompts when age < 18 (and shows a clear message).
"""

from datetime import datetime
import hashlib
import re
import traceback

# -------------------------
# Core in-memory data store
# -------------------------
accounts = {}
NEXT_ACCOUNT_START = 1001
PIN_RE = re.compile(r"^\d{4}$")

def generate_account_number():
    """Generate a unique account number string."""
    return str(NEXT_ACCOUNT_START + len(accounts))

def now_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -------------------------
# PIN helpers
# -------------------------
def hash_pin(pin: str) -> str:
    """Return SHA-256 hex digest of the pin string."""
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()

def validate_pin_format(pin: str):
    if not isinstance(pin, str) or not PIN_RE.fullmatch(pin):
        raise ValueError("PIN must be exactly 4 digits (numbers only).")

def set_pin(acct_no: str, pin: str):
    """Set or update PIN for an account (stores only hash)."""
    if acct_no not in accounts:
        raise ValueError("Account not found.")
    validate_pin_format(pin)
    accounts[acct_no]["pin_hash"] = hash_pin(pin)
    return True

def authenticate(acct_no: str, pin: str):
    """Return True if pin is correct for acct_no, else False. Raises ValueError if acct missing or pin not set."""
    if acct_no not in accounts:
        raise ValueError("Account not found.")
    acct = accounts[acct_no]
    if "pin_hash" not in acct or acct["pin_hash"] is None:
        raise ValueError("PIN not set for this account. Set a PIN before performing this action.")
    validate_pin_format(pin)
    return acct["pin_hash"] == hash_pin(pin)

# -------------------------
# Business logic functions (require PIN for sensitive ops)
# -------------------------
def create_account(name: str, age: int, pin: str = None):
    """
    Create a new account.
    Optionally provide a 4-digit pin to set it immediately.
    Returns account number string on success.
    Raises ValueError if validation fails.
    """
    name = str(name).strip()
    if not name:
        raise ValueError("Name cannot be empty.")
    if not isinstance(age, int):
        raise ValueError("Age must be an integer.")
    if age < 18:
        raise ValueError("Must be 18 or older to create account.")
    acct_no = generate_account_number()
    acct = {
        "name": name,
        "balance": 0.0,
        "transactions": [
            {"type": "ACCOUNT_CREATED", "amount": 0.0, "date": now_ts()}
        ],
        "pin_hash": None
    }
    accounts[acct_no] = acct
    if pin is not None:
        # validate and set
        set_pin(acct_no, pin)
    return acct_no

def deposit_money(acct_no: str, amount: float, pin: str):
    """
    Deposit amount into account. Requires PIN.
    Returns new balance.
    Raises ValueError for invalid account, invalid amount, invalid PIN.
    """
    if acct_no not in accounts:
        raise ValueError("Account not found.")
    # authenticate
    if not authenticate(acct_no, pin):
        raise ValueError("Invalid PIN.")
    try:
        amount = float(amount)
    except Exception:
        raise ValueError("Amount must be numeric.")
    if amount <= 0:
        raise ValueError("Deposit amount must be positive.")
    accounts[acct_no]["balance"] += round(amount, 2)
    accounts[acct_no]["transactions"].append({
        "type": "Deposit",
        "amount": round(amount, 2),
        "date": now_ts()
    })
    return accounts[acct_no]["balance"]

def withdraw_money(acct_no: str, amount: float, pin: str):
    """
    Withdraw amount from account. Requires PIN.
    Returns new balance.
    Raises ValueError for invalid account/amount, insufficient funds, or invalid PIN.
    """
    if acct_no not in accounts:
        raise ValueError("Account not found.")
    if not authenticate(acct_no, pin):
        raise ValueError("Invalid PIN.")
    try:
        amount = float(amount)
    except Exception:
        raise ValueError("Amount must be numeric.")
    if amount <= 0:
        raise ValueError("Withdrawal amount must be positive.")
    if amount > accounts[acct_no]["balance"]:
        raise ValueError("Insufficient balance.")
    accounts[acct_no]["balance"] -= round(amount, 2)
    accounts[acct_no]["transactions"].append({
        "type": "Withdrawal",
        "amount": round(amount, 2),
        "date": now_ts()
    })
    return accounts[acct_no]["balance"]

def view_balance(acct_no: str, pin: str):
    """Return the current balance for acct_no. Requires PIN."""
    if acct_no not in accounts:
        raise ValueError("Account not found.")
    if not authenticate(acct_no, pin):
        raise ValueError("Invalid PIN.")
    return accounts[acct_no]["balance"]

def transaction_history(acct_no: str, pin: str):
    """Return list of transactions for acct_no. Requires PIN."""
    if acct_no not in accounts:
        raise ValueError("Account not found.")
    if not authenticate(acct_no, pin):
        raise ValueError("Invalid PIN.")
    return list(accounts[acct_no]["transactions"])

# -------------------------
# Test harness (PIN flows)
# -------------------------
class TestCase:
    def __init__(self, tcid, scenario, passed=False, actual=""):
        self.tcid = tcid
        self.scenario = scenario
        self.passed = passed
        self.actual = actual

def run_tests():
    tests = []
    try:
        # TC01: Create account and set PIN during creation
        acct1 = create_account("Sai", 22, pin="1234")
        tests.append(TestCase("TC01", "Create account with PIN at creation", True, f"Created {acct1}"))
    except Exception as e:
        tests.append(TestCase("TC01", "Create account with PIN at creation", False, str(e)))

    try:
        # TC02: Attempt create account age < 18
        try:
            create_account("Ravi", 15)
            tests.append(TestCase("TC02", "Create account with age <18", False, "Account created unexpectedly"))
        except Exception as e:
            tests.append(TestCase("TC02", "Create account with age <18", True, str(e)))
    except Exception as e:
        tests.append(TestCase("TC02", "Create account with age <18", False, str(e)))

    try:
        # TC03: Deposit valid amount with correct PIN
        bal = deposit_money(acct1, 500, pin="1234")
        ok = abs(bal - 500) < 1e-9
        tests.append(TestCase("TC03", "Deposit valid amount with correct PIN", ok, f"Balance {bal:.2f}"))
    except Exception as e:
        tests.append(TestCase("TC03", "Deposit valid amount with correct PIN", False, str(e)))

    try:
        # TC04: Deposit negative amount (should fail)
        try:
            deposit_money(acct1, -200, pin="1234")
            tests.append(TestCase("TC04", "Deposit negative amount", False, "Negative deposit accepted"))
        except Exception as e:
            tests.append(TestCase("TC04", "Deposit negative amount", True, str(e)))
    except Exception as e:
        tests.append(TestCase("TC04", "Deposit negative amount", False, str(e)))

    try:
        # TC05: Withdraw amount less than balance with correct PIN
        new_bal = withdraw_money(acct1, 100, pin="1234")
        ok = abs(new_bal - 400) < 1e-9
        tests.append(TestCase("TC05", "Withdraw amount less than balance with correct PIN", ok, f"Balance {new_bal:.2f}"))
    except Exception as e:
        tests.append(TestCase("TC05", "Withdraw amount less than balance with correct PIN", False, str(e)))

    try:
        # TC06: Withdraw amount greater than balance (should fail)
        try:
            withdraw_money(acct1, 2000, pin="1234")
            tests.append(TestCase("TC06", "Withdraw amount greater than balance", False, "Over-withdrawal accepted"))
        except Exception as e:
            tests.append(TestCase("TC06", "Withdraw amount greater than balance", True, str(e)))
    except Exception as e:
        tests.append(TestCase("TC06", "Withdraw amount greater than balance", False, str(e)))

    try:
        # TC07: View balance with correct PIN
        try:
            b = view_balance(acct1, pin="1234")
            tests.append(TestCase("TC07", "View balance with correct PIN", abs(b - 400) < 1e-9, f"Balance {b:.2f}"))
        except Exception as e:
            tests.append(TestCase("TC07", "View balance with correct PIN", False, str(e)))
    except Exception as e:
        tests.append(TestCase("TC07", "View balance with correct PIN", False, str(e)))

    try:
        # TC08: Transaction history with correct PIN
        try:
            th = transaction_history(acct1, pin="1234")
            tests.append(TestCase("TC08", "Transaction history with correct PIN", len(th) >= 3, f"{len(th)} txns"))
        except Exception as e:
            tests.append(TestCase("TC08", "Transaction history with correct PIN", False, str(e)))
    except Exception as e:
        tests.append(TestCase("TC08", "Transaction history with correct PIN", False, str(e)))

    try:
        # TC09: Access with wrong PIN should fail
        try:
            view_balance(acct1, pin="0000")
            tests.append(TestCase("TC09", "View balance with wrong PIN", False, "Access granted with wrong PIN"))
        except Exception as e:
            tests.append(TestCase("TC09", "View balance with wrong PIN", True, str(e)))
    except Exception as e:
        tests.append(TestCase("TC09", "View balance with wrong PIN", False, str(e)))

    # Print report
    print("\n" + "="*72)
    print("TEST CASE EXECUTION REPORT (PIN-protected flows)")
    print("="*72)
    print(f"{'TCID':<6} {'Scenario':<45} {'Result':<6} {'Details'}")
    print("-"*72)
    for t in tests:
        print(f"{t.tcid:<6} {t.scenario:<45} {('PASS' if t.passed else 'FAIL'):<6} {t.actual}")
    print("="*72 + "\n")
    return tests

# -------------------------
# Interactive CLI (PIN-aware, fixed create flow)
# -------------------------
def interactive_mode():
    def print_line():
        print("-"*50)
    while True:
        print_line()
        print("🏦 Welcome to Simple Banking System (PIN-secured Interactive Mode)")
        print("1. Create New Account (optionally set PIN now)")
        print("2. Set / Update PIN for an account")
        print("3. Deposit Money (requires PIN)")
        print("4. Withdraw Money (requires PIN)")
        print("5. View Balance (requires PIN)")
        print("6. View Transaction History (requires PIN)")
        print("7. Run Automated Tests")
        print("8. Exit")
        print_line()
        choice = input("Enter your choice (1-8): ").strip()
        try:
            if choice == '1':
                # Loop create flow until success or user cancels
                while True:
                    print("\n(Enter 'c' at name prompt to cancel account creation)\n")
                    name = input("Enter full name: ").strip()
                    if name.lower() == 'c':
                        print("Account creation cancelled by user.")
                        break
                    age_input = input("Enter age: ").strip()
                    try:
                        age = int(age_input)
                    except ValueError:
                        print("Invalid age input. Please enter a valid integer age.")
                        continue
                    # If age < 18, show message and restart creation flow
                    if age < 18:
                        print("Age is not over 18. You cannot create account.")
                        # restart (continue loop)
                        continue
                    # Age OK -- ask whether to set PIN now
                    create_now = input("Do you want to set a 4-digit PIN now? (y/n): ").strip().lower()
                    if create_now == 'y':
                        while True:
                            pin = input("Enter 4-digit PIN: ").strip()
                            pin2 = input("Confirm PIN: ").strip()
                            try:
                                if pin != pin2:
                                    print("Pins do not match. Try again.")
                                    continue
                                validate_pin_format(pin)
                                acct = create_account(name, age, pin=pin)
                                print(f"✅ Account created: {acct} (PIN set)")
                                break
                            except Exception as e:
                                print("Error:", e)
                        break  # exit create loop after successful creation
                    else:
                        # create without PIN
                        try:
                            acct = create_account(name, age, pin=None)
                            print(f"✅ Account created: {acct} (No PIN set). Use option 2 to set PIN.")
                            break
                        except Exception as e:
                            print("Error:", e)
                            # if some other validation fails, restart loop
                            continue

            elif choice == '2':
                acc = input("Account number: ").strip()
                while True:
                    pin = input("Enter new 4-digit PIN: ").strip()
                    pin2 = input("Confirm PIN: ").strip()
                    try:
                        if pin != pin2:
                            print("Pins do not match. Try again.")
                            continue
                        set_pin(acc, pin)
                        print("✅ PIN set/updated successfully.")
                        break
                    except Exception as e:
                        print("Error:", e)
            elif choice == '3':
                acc = input("Account number: ").strip()
                pin = input("Enter 4-digit PIN: ").strip()
                amt = float(input("Amount to deposit: ").strip())
                bal = deposit_money(acc, amt, pin=pin)
                print(f"✅ Deposited ₹{amt:.2f}. New balance: ₹{bal:.2f}")
            elif choice == '4':
                acc = input("Account number: ").strip()
                pin = input("Enter 4-digit PIN: ").strip()
                amt = float(input("Amount to withdraw: ").strip())
                bal = withdraw_money(acc, amt, pin=pin)
                print(f"✅ Withdrawn ₹{amt:.2f}. New balance: ₹{bal:.2f}")
            elif choice == '5':
                acc = input("Account number: ").strip()
                pin = input("Enter 4-digit PIN: ").strip()
                bal = view_balance(acc, pin=pin)
                print(f"💰 Current balance: ₹{bal:.2f}")
            elif choice == '6':
                acc = input("Account number: ").strip()
                pin = input("Enter 4-digit PIN: ").strip()
                th = transaction_history(acc, pin=pin)
                print(f"📜 Transaction history for {acc}:")
                for t in th:
                    print(f"  {t['date']} - {t['type']}: ₹{t['amount']:.2f}")
            elif choice == '7':
                run_tests()
            elif choice == '8':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Enter 1-8.")
        except Exception as e:
            print("Error:", e)
            # traceback.print_exc()

# -------------------------
# MAIN MODE SETTINGS
# -------------------------
# Options: "tests_then_interactive", "interactive_only", "tests_only"
MAIN_MODE = "tests_then_interactive"

# -------------------------
# Main guard
# -------------------------
if __name__ == "__main__":
    if MAIN_MODE == "tests_then_interactive":
        run_tests()
        interactive_mode()
    elif MAIN_MODE == "interactive_only":
        interactive_mode()
    elif MAIN_MODE == "tests_only":
        run_tests()
    else:
        print("Invalid MAIN_MODE. Set MAIN_MODE to one of: tests_then_interactive, interactive_only, tests_only")

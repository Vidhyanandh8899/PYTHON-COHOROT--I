# PYTHON-COHOROT--I



. Problem Statement
The objective of this project is to develop a text-based banking system using Python that allows users to perform basic banking operations through a command-line interface. The system enables users to create accounts, deposit and withdraw money, check account balances, and view transaction history. The project reinforces Python concepts such as functions, loops, dictionaries, exception handling, and user input validation.
2. Approach
The project follows a modular approach where each feature is implemented as a function. It uses a dictionary to store account data, ensuring quick access and modification. Input validation and exception handling ensure reliability and prevent invalid user inputs.
3. Technologies Used
Component	Description
Language	Python 3
Modules Used	datetime, sys
Data Structure	Dictionary
IDE Used	VS Code / PyCharm
Interface	Command-line (Text-based)
4. Code Explanation
The system includes the following main functions:
•	create_account() –
Creates a new bank account after verifying that the user’s age is 18 or above.
Optionally allows the user to set a 4-digit security PIN during account creation.
•	set_pin() –
Lets the user create or update a 4-digit PIN for securing the account.
The PIN is stored in encrypted (hashed) format for security.
•	authenticate() –
Verifies whether the entered PIN matches the stored hashed PIN before allowing any banking transaction.
•	deposit_money() –
Allows the user to deposit money into their account after successful PIN verification.
Ensures that the entered amount is positive.
•	withdraw_money() –
Allows the user to withdraw money from their account after entering the correct PIN.
Checks if the account has sufficient balance before processing the withdrawal.
•	view_balance() –
Displays the current balance of the user’s account after PIN verification.
•	transaction_history() –
Displays all previous transactions (deposits, withdrawals, and account creation) along with date and time.
•	run_tests() –
Automatically runs predefined test cases to verify all major functions such as account creation, deposit, withdrawal, and PIN verification.
•	interactive_mode() –
Provides a menu-driven interface that allows the user to perform all banking operations such as creating accounts, setting PINs, depositing, withdrawing, and viewing balances interactively.


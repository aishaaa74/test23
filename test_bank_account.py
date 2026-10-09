"""
Модульные тесты для класса BankAccount.

Запуск:
    python -m unittest test_bank_account.py -v
или просто:
    python test_bank_account.py
"""

import unittest

from bank_account import (
    BankAccount,
    InvalidAmountError,
    InsufficientFundsError,
)


class TestBankAccountCreation(unittest.TestCase):
    """Тесты создания банковского счёта."""

    def test_create_account_stores_owner_and_number(self):
        account = BankAccount("Иван Иванов", "40817810000000001")
        self.assertEqual(account.owner, "Иван Иванов")
        self.assertEqual(account.account_number, "40817810000000001")

    def test_new_account_has_zero_balance(self):
        account = BankAccount("Иван Иванов", "40817810000000001")
        self.assertEqual(account.get_balance(), 0)

    def test_new_account_is_empty(self):
        account = BankAccount("Иван Иванов", "40817810000000001")
        self.assertTrue(account.is_empty())

    def test_create_account_with_empty_owner_raises_error(self):
        with self.assertRaises(ValueError):
            BankAccount("", "40817810000000001")

    def test_create_account_with_empty_number_raises_error(self):
        with self.assertRaises(ValueError):
            BankAccount("Иван Иванов", "")

    def test_create_account_with_non_string_owner_raises_error(self):
        with self.assertRaises(ValueError):
            BankAccount(12345, "40817810000000001")


class TestDeposit(unittest.TestCase):
    """Тесты пополнения счёта."""

    def setUp(self):
        self.account = BankAccount("Иван Иванов", "40817810000000001")

    def test_deposit_increases_balance(self):
        self.account.deposit(1000)
        self.assertEqual(self.account.get_balance(), 1000)

    def test_multiple_deposits_accumulate(self):
        self.account.deposit(500)
        self.account.deposit(250.5)
        self.assertEqual(self.account.get_balance(), 750.5)

    def test_deposit_zero_raises_error(self):
        with self.assertRaises(InvalidAmountError):
            self.account.deposit(0)

    def test_deposit_negative_amount_raises_error(self):
        with self.assertRaises(InvalidAmountError):
            self.account.deposit(-100)

    def test_deposit_non_numeric_amount_raises_error(self):
        with self.assertRaises(InvalidAmountError):
            self.account.deposit("сто рублей")

    def test_deposit_invalid_amount_does_not_change_balance(self):
        self.account.deposit(100)
        with self.assertRaises(InvalidAmountError):
            self.account.deposit(-50)
        self.assertEqual(self.account.get_balance(), 100)


class TestWithdraw(unittest.TestCase):
    """Тесты снятия денежных средств."""

    def setUp(self):
        self.account = BankAccount("Иван Иванов", "40817810000000001")
        self.account.deposit(1000)

    def test_withdraw_decreases_balance(self):
        self.account.withdraw(400)
        self.assertEqual(self.account.get_balance(), 600)

    def test_withdraw_full_balance_makes_account_empty(self):
        self.account.withdraw(1000)
        self.assertTrue(self.account.is_empty())

    def test_withdraw_more_than_balance_raises_error(self):
        with self.assertRaises(InsufficientFundsError):
            self.account.withdraw(1500)

    def test_withdraw_more_than_balance_does_not_change_balance(self):
        with self.assertRaises(InsufficientFundsError):
            self.account.withdraw(1500)
        self.assertEqual(self.account.get_balance(), 1000)

    def test_withdraw_negative_amount_raises_error(self):
        with self.assertRaises(InvalidAmountError):
            self.account.withdraw(-200)

    def test_withdraw_zero_raises_error(self):
        with self.assertRaises(InvalidAmountError):
            self.account.withdraw(0)


class TestTransfer(unittest.TestCase):
    """Тесты перевода денежных средств между счетами."""

    def setUp(self):
        self.sender = BankAccount("Иван Иванов", "40817810000000001")
        self.receiver = BankAccount("Пётр Петров", "40817810000000002")
        self.sender.deposit(1000)

    def test_transfer_decreases_sender_balance(self):
        self.sender.transfer(self.receiver, 300)
        self.assertEqual(self.sender.get_balance(), 700)

    def test_transfer_increases_receiver_balance(self):
        self.sender.transfer(self.receiver, 300)
        self.assertEqual(self.receiver.get_balance(), 300)

    def test_transfer_amount_is_equal_on_both_sides(self):
        sender_before = self.sender.get_balance()
        receiver_before = self.receiver.get_balance()
        self.sender.transfer(self.receiver, 300)
        sender_change = sender_before - self.sender.get_balance()
        receiver_change = self.receiver.get_balance() - receiver_before
        self.assertEqual(sender_change, receiver_change)

    def test_transfer_insufficient_funds_raises_error(self):
        with self.assertRaises(InsufficientFundsError):
            self.sender.transfer(self.receiver, 5000)

    def test_transfer_insufficient_funds_does_not_change_balances(self):
        with self.assertRaises(InsufficientFundsError):
            self.sender.transfer(self.receiver, 5000)
        self.assertEqual(self.sender.get_balance(), 1000)
        self.assertEqual(self.receiver.get_balance(), 0)

    def test_transfer_invalid_amount_does_not_change_balances(self):
        with self.assertRaises(InvalidAmountError):
            self.sender.transfer(self.receiver, -100)
        self.assertEqual(self.sender.get_balance(), 1000)
        self.assertEqual(self.receiver.get_balance(), 0)

    def test_transfer_to_non_account_raises_error(self):
        with self.assertRaises(TypeError):
            self.sender.transfer("не счёт", 100)

    def test_transfer_to_same_account_raises_error(self):
        with self.assertRaises(ValueError):
            self.sender.transfer(self.sender, 100)


class TestGetBalance(unittest.TestCase):
    """Тесты получения текущего баланса."""

    def test_balance_reflects_sequence_of_operations(self):
        account = BankAccount("Иван Иванов", "40817810000000001")
        account.deposit(1000)
        account.withdraw(200)
        account.deposit(50)
        self.assertEqual(account.get_balance(), 850)


class TestIsEmpty(unittest.TestCase):
    """Тесты проверки пустого счёта."""

    def test_new_account_is_empty(self):
        account = BankAccount("Иван Иванов", "40817810000000001")
        self.assertTrue(account.is_empty())

    def test_account_with_balance_is_not_empty(self):
        account = BankAccount("Иван Иванов", "40817810000000001")
        account.deposit(100)
        self.assertFalse(account.is_empty())

    def test_account_becomes_empty_after_full_withdrawal(self):
        account = BankAccount("Иван Иванов", "40817810000000001")
        account.deposit(100)
        account.withdraw(100)
        self.assertTrue(account.is_empty())


if __name__ == "__main__":
    unittest.main(verbosity=2)
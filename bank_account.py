"""
Модуль банковского счёта.

Содержит класс BankAccount, реализующий базовые банковские операции:
создание счёта, пополнение, снятие средств, перевод между счетами,
получение баланса и проверку на пустоту счёта.
"""


class BankAccountError(Exception):
    """Базовое исключение для ошибок, связанных с банковским счётом."""
    pass


class InvalidAmountError(BankAccountError):
    """Сумма операции некорректна (не число, ноль или отрицательное значение)."""
    pass


class InsufficientFundsError(BankAccountError):
    """На счёте недостаточно средств для выполнения операции."""
    pass


class BankAccount:
    """Представляет банковский счёт с владельцем, номером и балансом."""

    def __init__(self, owner: str, account_number: str):
        """
        Создаёт новый банковский счёт с нулевым начальным балансом.

        :param owner: имя владельца счёта (непустая строка)
        :param account_number: номер счёта (непустая строка)
        :raises ValueError: если owner или account_number некорректны
        """
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("Имя владельца должно быть непустой строкой")
        if not isinstance(account_number, str) or not account_number.strip():
            raise ValueError("Номер счёта должен быть непустой строкой")

        self._owner = owner
        self._account_number = account_number
        self._balance = 0

    # ---------- Свойства (только чтение) ----------

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def account_number(self) -> str:
        return self._account_number

    # ---------- Вспомогательная валидация ----------

    @staticmethod
    def _validate_amount(amount) -> None:
        """Проверяет, что сумма — положительное число."""
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise InvalidAmountError("Сумма должна быть числом")
        if amount <= 0:
            raise InvalidAmountError("Сумма должна быть больше нуля")

    # ---------- Основные операции ----------

    def deposit(self, amount) -> None:
        """
        Пополняет счёт на указанную сумму.

        :param amount: сумма пополнения (положительное число)
        :raises InvalidAmountError: если сумма некорректна
        """
        self._validate_amount(amount)
        self._balance += amount

    def withdraw(self, amount) -> None:
        """
        Снимает указанную сумму со счёта.

        :param amount: сумма снятия (положительное число)
        :raises InvalidAmountError: если сумма некорректна
        :raises InsufficientFundsError: если средств недостаточно
        """
        self._validate_amount(amount)
        if amount > self._balance:
            raise InsufficientFundsError(
                "Недостаточно средств для снятия указанной суммы"
            )
        self._balance -= amount

    def transfer(self, other_account: "BankAccount", amount) -> None:
        """
        Переводит указанную сумму на другой счёт.

        Если перевод невозможен (некорректная сумма, недостаточно средств,
        некорректный счёт-получатель), состояние обоих счетов не меняется.

        :param other_account: счёт-получатель (экземпляр BankAccount)
        :param amount: сумма перевода (положительное число)
        :raises TypeError: если other_account не является BankAccount
        :raises InvalidAmountError: если сумма некорректна
        :raises InsufficientFundsError: если средств недостаточно
        """
        if not isinstance(other_account, BankAccount):
            raise TypeError("Получатель перевода должен быть объектом BankAccount")
        if other_account is self:
            raise ValueError("Нельзя перевести средства на тот же самый счёт")

        # validate_amount и проверка баланса выполняются до изменения
        # состояния счетов, поэтому при ошибке оба счёта остаются нетронутыми.
        self._validate_amount(amount)
        if amount > self._balance:
            raise InsufficientFundsError(
                "Недостаточно средств для перевода указанной суммы"
            )

        self._balance -= amount
        other_account._balance += amount

    def get_balance(self):
        """Возвращает текущий баланс счёта."""
        return self._balance

    def is_empty(self) -> bool:
        """Возвращает True, если баланс счёта равен нулю."""
        return self._balance == 0

    def __repr__(self) -> str:
        return (
            f"BankAccount(owner={self._owner!r}, "
            f"account_number={self._account_number!r}, "
            f"balance={self._balance!r})"
        )
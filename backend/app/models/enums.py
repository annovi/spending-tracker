import enum


class CategoryType(str, enum.Enum):
    expense = "expense"
    income = "income"


class AccountType(str, enum.Enum):
    bank = "bank"
    credit_card = "credit_card"
    cash = "cash"

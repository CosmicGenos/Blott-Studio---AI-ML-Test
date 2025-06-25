from enum import Enum


class PaymentMethodType(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"


class RecommendedAction(str, Enum):
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"


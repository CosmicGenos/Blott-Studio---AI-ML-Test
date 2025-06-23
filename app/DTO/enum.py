from enum import Enum


class PaymentMethodType(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RecommendedAction(str, Enum):
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"

class ConfigType(str, Enum):
    COUNTRY_RISK = "country_risk"
    BUSINESS_HOURS = "business_hours"
    AMOUNT_THRESHOLD = "amount_threshold"
    VELOCITY_LIMIT = "velocity_limit"
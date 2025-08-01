"""
Pydantic schemas for request/response validation.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class TransactionType(str, Enum):
    """Transaction types."""
    PURCHASE = "purchase"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    DEPOSIT = "deposit"
    PAYMENT = "payment"
    REFUND = "refund"


class PaymentMethod(str, Enum):
    """Payment method types."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CASH = "cash"
    CHECK = "check"


class RiskLevel(str, Enum):
    """Risk levels for fraud scoring."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TransactionBase(BaseModel):
    """Base transaction schema."""
    transaction_id: str = Field(..., min_length=1, max_length=100)
    user_id: str = Field(..., min_length=1, max_length=100)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(..., min_length=3, max_length=3)
    transaction_type: TransactionType
    payment_method: PaymentMethod
    merchant_id: Optional[str] = Field(None, max_length=100)
    merchant_category: Optional[str] = Field(None, max_length=10)
    location: Optional[str] = Field(None, max_length=200)
    device_fingerprint: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    timestamp: Optional[datetime] = None
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        """Validate currency code."""
        if not v.isupper() or len(v) != 3:
            raise ValueError('Currency must be a 3-letter uppercase code')
        return v
    
    @field_validator('merchant_category')
    @classmethod
    def validate_merchant_category(cls, v):
        """Validate merchant category code."""
        if v and not v.isdigit():
            raise ValueError('Merchant category must be numeric')
        return v


class TransactionCreate(TransactionBase):
    """Schema for creating transactions."""
    pass


class FraudDetectionRequest(BaseModel):
    """Schema for fraud detection requests."""
    transaction_id: str
    user_id: str
    amount: float
    merchant_category: str
    transaction_type: str
    timestamp: datetime
    location: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None


class FraudDetectionResponse(BaseModel):
    """Schema for fraud detection responses."""
    transaction_id: str
    fraud_score: float = Field(..., ge=0, le=1)
    is_fraud: bool
    risk_level: str
    reasons: List[str]
    recommendations: List[str]
    correlation_id: str
    processing_time_ms: int


class FraudPrediction(BaseModel):
    """Schema for fraud prediction results."""
    is_fraud: bool
    fraud_probability: float = Field(..., ge=0, le=1)
    risk_level: RiskLevel
    confidence_score: float = Field(..., ge=0, le=1)
    reasons: List[str] = []
    recommendations: List[str] = []


class BatchFraudDetectionRequest(BaseModel):
    """Schema for batch fraud detection requests."""
    transactions: List[FraudDetectionRequest]
    correlation_id: Optional[str] = None


class BatchFraudDetectionResponse(BaseModel):
    """Schema for batch fraud detection responses."""
    results: List[FraudDetectionResponse]
    total_processed: int
    correlation_id: str


class HealthCheck(BaseModel):
    """Schema for health check responses."""
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: Optional[int] = None


class SystemMetrics(BaseModel):
    """Schema for system metrics."""
    total_requests: int
    fraud_detections: int
    fraud_rate: float
    avg_response_time_ms: float
    model_version: Optional[str] = None
    last_model_update: Optional[datetime] = None


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class Token(BaseModel):
    """Schema for authentication tokens."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    message: str
    correlation_id: Optional[str] = None
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

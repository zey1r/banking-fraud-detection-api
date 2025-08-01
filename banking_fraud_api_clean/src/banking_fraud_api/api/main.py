"""
Banking Fraud Detection API
Enterprise-grade fraud detection system
"""

import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import uvicorn

from banking_fraud_api.core.config import settings
from banking_fraud_api.core.enterprise_security import enterprise_security, audit_logger, SecurityException

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# Pydantic models
class FraudDetectionRequest(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    merchant_category: str
    transaction_type: str
    timestamp: datetime
    location: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None


class FraudDetectionResponse(BaseModel):
    transaction_id: str
    fraud_score: float
    is_fraud: bool
    risk_level: str
    reasons: List[str]
    recommendations: List[str]
    correlation_id: str
    processing_time_ms: int


class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str


class SystemMetrics(BaseModel):
    total_requests: int
    fraud_detections: int
    fraud_rate: float
    avg_response_time_ms: float


def get_correlation_id() -> str:
    """Generate correlation ID for request tracking."""
    return str(uuid.uuid4())


@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add correlation ID to each request."""
    correlation_id = get_correlation_id()
    request.state.correlation_id = correlation_id
    
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    
    return response


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "🏦 Banking Fraud Detection API",
        "status": "online",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.VERSION
    )


@app.get("/metrics", response_model=SystemMetrics)
async def get_metrics():
    """Get system metrics."""
    # Mock metrics - in production, these would come from monitoring
    return SystemMetrics(
        total_requests=10000,
        fraud_detections=150,
        fraud_rate=0.015,
        avg_response_time_ms=85.5
    )


@app.post(f"{settings.API_V1_STR}/fraud/detect", response_model=FraudDetectionResponse)
async def detect_fraud(
    request: FraudDetectionRequest,
    http_request: Request,
    background_tasks: BackgroundTasks
):
    """
    Detect fraud for a single transaction.
    
    This endpoint analyzes a transaction and returns fraud probability,
    risk level, and recommendations.
    """
    start_time = time.time()
    correlation_id = http_request.state.correlation_id
    
    try:
        logger.info(
            f"Processing fraud detection request",
            extra={
                "correlation_id": correlation_id,
                "transaction_id": request.transaction_id,
                "user_id": request.user_id,
                "amount": request.amount
            }
        )
        
        # Log security event
        audit_logger.log_security_event(
            event_type="fraud_detection_request",
            user_id=request.user_id,
            details={
                "transaction_id": request.transaction_id,
                "amount": request.amount,
                "correlation_id": correlation_id
            },
            risk_level="INFO"
        )
        
        # Simple fraud detection logic (replace with ML model)
        fraud_score = calculate_fraud_score(request)
        is_fraud = fraud_score >= settings.FRAUD_THRESHOLD_MEDIUM
        
        # Determine risk level
        if fraud_score >= settings.FRAUD_THRESHOLD_CRITICAL:
            risk_level = "CRITICAL"
        elif fraud_score >= settings.FRAUD_THRESHOLD_HIGH:
            risk_level = "HIGH"
        elif fraud_score >= settings.FRAUD_THRESHOLD_MEDIUM:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Generate reasons and recommendations
        reasons = generate_reasons(request, fraud_score)
        recommendations = generate_recommendations(risk_level)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        response = FraudDetectionResponse(
            transaction_id=request.transaction_id,
            fraud_score=fraud_score,
            is_fraud=is_fraud,
            risk_level=risk_level,
            reasons=reasons,
            recommendations=recommendations,
            correlation_id=correlation_id,
            processing_time_ms=processing_time
        )
        
        # Log result
        logger.info(
            f"Fraud detection completed",
            extra={
                "correlation_id": correlation_id,
                "transaction_id": request.transaction_id,
                "fraud_score": fraud_score,
                "is_fraud": is_fraud,
                "risk_level": risk_level
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(
            f"Error in fraud detection",
            extra={
                "correlation_id": correlation_id,
                "transaction_id": request.transaction_id,
                "error": str(e)
            },
            exc_info=True
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal error processing fraud detection: {str(e)}"
        )


@app.post(f"{settings.API_V1_STR}/fraud/detect/batch")
async def detect_fraud_batch(
    requests: List[FraudDetectionRequest],
    http_request: Request
):
    """Detect fraud for multiple transactions."""
    correlation_id = http_request.state.correlation_id
    
    if len(requests) > 100:  # Limit batch size
        raise HTTPException(
            status_code=400,
            detail="Batch size too large. Maximum 100 transactions per request."
        )
    
    results = []
    for req in requests:
        # Process each request (simplified)
        fraud_score = calculate_fraud_score(req)
        results.append({
            "transaction_id": req.transaction_id,
            "fraud_score": fraud_score,
            "is_fraud": fraud_score >= settings.FRAUD_THRESHOLD_MEDIUM
        })
    
    return {"results": results, "correlation_id": correlation_id}


def calculate_fraud_score(request: FraudDetectionRequest) -> float:
    """
    Calculate fraud score based on transaction data.
    This is a simplified version - replace with ML model.
    """
    score = 0.0
    
    # Amount-based scoring
    if request.amount > float(settings.SUSPICIOUS_AMOUNT_THRESHOLD):
        score += 0.3
    
    if request.amount > float(settings.HIGH_AMOUNT_THRESHOLD):
        score += 0.2
    
    # Time-based scoring
    if request.timestamp:
        hour = request.timestamp.hour
        if hour < 6 or hour > 22:  # Late night transactions
            score += 0.2
    
    # Merchant category scoring
    high_risk_categories = ["gambling", "cryptocurrency", "adult_content"]
    if request.merchant_category.lower() in high_risk_categories:
        score += 0.4
    
    # Location-based scoring
    if request.location and "unknown" in request.location.lower():
        score += 0.3
    
    return min(score, 1.0)


def generate_reasons(request: FraudDetectionRequest, fraud_score: float) -> List[str]:
    """Generate reasons for fraud score."""
    reasons = []
    
    if request.amount > float(settings.SUSPICIOUS_AMOUNT_THRESHOLD):
        reasons.append("High transaction amount")
    
    if request.timestamp and (request.timestamp.hour < 6 or request.timestamp.hour > 22):
        reasons.append("Unusual transaction time")
    
    if fraud_score > settings.FRAUD_THRESHOLD_HIGH:
        reasons.append("Multiple risk factors detected")
    
    if not reasons:
        reasons.append("Transaction appears normal")
    
    return reasons


def generate_recommendations(risk_level: str) -> List[str]:
    """Generate recommendations based on risk level."""
    if risk_level == "CRITICAL":
        return [
            "Block transaction immediately",
            "Contact customer via secure channel",
            "Review recent account activity"
        ]
    elif risk_level == "HIGH":
        return [
            "Require additional authentication",
            "Review transaction details manually",
            "Monitor future transactions closely"
        ]
    elif risk_level == "MEDIUM":
        return [
            "Consider additional verification",
            "Log transaction for review"
        ]
    else:
        return ["Process transaction normally"]


@app.exception_handler(SecurityException)
async def security_exception_handler(request: Request, exc: SecurityException):
    """Handle security exceptions."""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    logger.warning(
        f"Security exception: {str(exc)}",
        extra={"correlation_id": correlation_id}
    )
    
    return JSONResponse(
        status_code=403,
        content={
            "error": "Security violation",
            "message": str(exc),
            "correlation_id": correlation_id
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

"""Main FastAPI application module."""

import os
import time

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.app import __version__
from src.app.services import calculate_discount, process_order_summary

app = FastAPI(
    title="CI/CD Demo Service",
    description="Production-ready FastAPI service illustrating automated CI/CD lifecycle",
    version=__version__,
)

START_TIME = time.time()


# Request & Response Models
class OrderItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderRequest(BaseModel):
    items: list[OrderItem]
    tax_rate: float = Field(default=0.08, ge=0, le=1)


class DiscountRequest(BaseModel):
    price: float = Field(..., gt=0)
    discount_percent: float = Field(..., ge=0, le=100)


@app.get("/")
def read_root():
    """Root landing endpoint."""
    return {
        "status": "online",
        "service": "ci-cd-demo-service",
        "version": __version__,
        "environment": os.getenv("APP_ENV", "development"),
        "docs_url": "/docs",
    }


@app.get("/health/live", status_code=status.HTTP_200_OK)
def liveness_probe():
    """Kubernetes/Container liveness probe to verify app process is running."""
    return {"status": "alive", "uptime_seconds": round(time.time() - START_TIME, 2)}


@app.get("/health/ready", status_code=status.HTTP_200_OK)
def readiness_probe():
    """Kubernetes/Load-balancer readiness probe to verify service is ready to take traffic."""
    # In production, check database, cache, or external dependency connectivity here
    return {
        "status": "ready",
        "version": __version__,
        "database": "connected",
    }


@app.get("/version")
def get_version():
    """Returns application release version and commit SHA."""
    return {
        "version": __version__,
        "commit_sha": os.getenv("GIT_COMMIT_SHA", "unknown"),
        "environment": os.getenv("APP_ENV", "development"),
    }


@app.post("/api/v1/discounts/calculate")
def post_discount(req: DiscountRequest):
    """Calculates discounted price."""
    try:
        discounted = calculate_discount(req.price, req.discount_percent)
        return {
            "original_price": req.price,
            "discount_percent": req.discount_percent,
            "final_price": discounted,
        }
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.post("/api/v1/orders/calculate")
def post_order_summary(req: OrderRequest):
    """Processes order items and computes summary."""
    try:
        items_dict = [item.model_dump() for item in req.items]
        summary = process_order_summary(items_dict, tax_rate=req.tax_rate)
        return summary
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

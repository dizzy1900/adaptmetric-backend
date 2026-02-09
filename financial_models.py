# =============================================================================
# Financial Models - Pydantic Schemas for Financial Analysis
# =============================================================================

from pydantic import BaseModel, Field
from typing import Optional


class FinancialParams(BaseModel):
    """
    Financial parameters for ROI analysis.
    
    These parameters define the economic context for evaluating
    climate resilience investments.
    """
    discount_rate_pct: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Discount rate as percentage (e.g., 10.0 for 10%)"
    )
    analysis_period_years: int = Field(
        ...,
        ge=1,
        le=100,
        description="Time horizon for analysis in years (e.g., 20)"
    )
    currency: str = Field(
        default='USD',
        description="Currency code (ISO 4217 format)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "discount_rate_pct": 10.0,
                "analysis_period_years": 20,
                "currency": "USD"
            }
        }


class ProjectCosts(BaseModel):
    """
    Project cost structure for climate resilience investments.
    
    Separates upfront capital expenditure from ongoing operational costs.
    """
    capex_initial: float = Field(
        ...,
        ge=0.0,
        description="Initial capital expenditure (upfront cost)"
    )
    opex_annual: float = Field(
        ...,
        ge=0.0,
        description="Annual operational and maintenance cost"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "capex_initial": 100000.0,
                "opex_annual": 5000.0
            }
        }


class CashFlowRequest(BaseModel):
    """
    Request model for financial calculations.
    
    Used by the /calculate-financials endpoint for testing.
    """
    cash_flows: list[float] = Field(
        ...,
        min_length=2,
        description="List of yearly cash flows (Year 0 is typically negative CAPEX)"
    )
    discount_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Discount rate as decimal (e.g., 0.10 for 10%)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "cash_flows": [-100000, 15000, 15000, 15000, 15000, 15000],
                "discount_rate": 0.10
            }
        }


class ROIMetrics(BaseModel):
    """
    Return on Investment metrics for financial analysis.
    
    Provides key financial indicators for decision-making.
    """
    npv: float = Field(
        ...,
        description="Net Present Value (NPV) in currency units"
    )
    bcr: float = Field(
        ...,
        description="Benefit-Cost Ratio (BCR) - ratio of PV benefits to PV costs"
    )
    payback_period_years: Optional[float] = Field(
        None,
        description="Years until cumulative cash flow turns positive (None if never positive)"
    )
    irr: Optional[float] = Field(
        None,
        description="Internal Rate of Return (IRR) as decimal (optional)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "npv": 56862.0,
                "bcr": 1.57,
                "payback_period_years": 6.67,
                "irr": 0.15
            }
        }

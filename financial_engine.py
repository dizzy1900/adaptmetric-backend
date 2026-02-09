# =============================================================================
# Financial Engine - ROI and NPV Calculations
# =============================================================================

from typing import Optional, List, Tuple


def calculate_npv(cash_flows: List[float], discount_rate: float) -> float:
    """
    Calculate Net Present Value (NPV).
    
    NPV = Σ (Cash Flow_t / (1 + r)^t) for t = 0 to n
    
    Args:
        cash_flows: List of yearly cash flows (Year 0 = initial investment, usually negative)
        discount_rate: Discount rate as decimal (e.g., 0.10 for 10%)
    
    Returns:
        Net Present Value in currency units
    """
    npv = 0.0
    for t, cash_flow in enumerate(cash_flows):
        npv += cash_flow / ((1 + discount_rate) ** t)
    
    return npv


def calculate_bcr(cash_flows: List[float], discount_rate: float) -> float:
    """
    Calculate Benefit-Cost Ratio (BCR).
    
    BCR = PV(Positive Cash Flows) / PV(Negative Cash Flows)
    
    A BCR > 1 indicates benefits exceed costs.
    
    Args:
        cash_flows: List of yearly cash flows
        discount_rate: Discount rate as decimal (e.g., 0.10 for 10%)
    
    Returns:
        Benefit-Cost Ratio (dimensionless)
    """
    pv_benefits = 0.0
    pv_costs = 0.0
    
    for t, cash_flow in enumerate(cash_flows):
        discount_factor = (1 + discount_rate) ** t
        
        if cash_flow > 0:
            pv_benefits += cash_flow / discount_factor
        else:
            pv_costs += abs(cash_flow) / discount_factor
    
    # Avoid division by zero
    if pv_costs == 0:
        return float('inf') if pv_benefits > 0 else 0.0
    
    return pv_benefits / pv_costs


def calculate_payback_period(cash_flows: List[float]) -> Optional[float]:
    """
    Calculate Payback Period (simple, undiscounted).
    
    Payback Period = Year when cumulative cash flow turns positive
    
    Uses linear interpolation for fractional years.
    
    Args:
        cash_flows: List of yearly cash flows
    
    Returns:
        Years until payback (float) or None if never positive
    """
    cumulative = 0.0
    
    for year, cash_flow in enumerate(cash_flows):
        cumulative += cash_flow
        
        # Check if cumulative just turned positive
        if cumulative >= 0:
            # If it turned positive in year 0, return 0
            if year == 0:
                return 0.0
            
            # Linear interpolation for fractional year
            # Cumulative at previous year
            cumulative_previous = cumulative - cash_flow
            
            # Fraction of current year needed
            if cash_flow != 0:
                fraction = abs(cumulative_previous) / cash_flow
                return year - 1 + fraction
            else:
                return float(year)
    
    # Never reached positive cumulative cash flow
    return None


def calculate_roi_metrics(cash_flows: List[float], discount_rate: float) -> dict:
    """
    Calculate comprehensive ROI metrics.
    
    Provides NPV, BCR, and Payback Period for financial decision-making.
    
    Args:
        cash_flows: List of yearly cash flows (Year 0 = initial investment, usually negative)
        discount_rate: Discount rate as decimal (e.g., 0.10 for 10%)
    
    Returns:
        Dictionary with:
        - 'npv': Net Present Value
        - 'bcr': Benefit-Cost Ratio
        - 'payback_period_years': Years to payback (or None)
    
    Example:
        >>> cash_flows = [-100000, 15000, 15000, 15000, 15000, 15000]
        >>> discount_rate = 0.10
        >>> metrics = calculate_roi_metrics(cash_flows, discount_rate)
        >>> print(f"NPV: ${metrics['npv']:,.2f}")
        >>> print(f"BCR: {metrics['bcr']:.2f}")
        >>> print(f"Payback: {metrics['payback_period_years']:.2f} years")
    """
    # Calculate NPV
    npv = calculate_npv(cash_flows, discount_rate)
    
    # Calculate BCR
    bcr = calculate_bcr(cash_flows, discount_rate)
    
    # Calculate Payback Period
    payback_period = calculate_payback_period(cash_flows)
    
    return {
        'npv': round(npv, 2),
        'bcr': round(bcr, 2),
        'payback_period_years': round(payback_period, 2) if payback_period is not None else None
    }


def generate_cash_flows(
    capex_initial: float,
    opex_annual: float,
    benefit_annual: float,
    analysis_period_years: int
) -> List[float]:
    """
    Generate cash flow series from cost and benefit parameters.
    
    Useful helper function to create cash flow arrays from project parameters.
    
    Args:
        capex_initial: Initial capital expenditure (negative outflow)
        opex_annual: Annual operational cost (negative outflow)
        benefit_annual: Annual benefit (positive inflow)
        analysis_period_years: Number of years to project
    
    Returns:
        List of cash flows [Year 0, Year 1, ..., Year N]
    """
    cash_flows = []
    
    # Year 0: Initial CAPEX (negative)
    cash_flows.append(-capex_initial)
    
    # Years 1 to N: Net annual cash flow (benefit - opex)
    for year in range(1, analysis_period_years + 1):
        net_annual = benefit_annual - opex_annual
        cash_flows.append(net_annual)
    
    return cash_flows

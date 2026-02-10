# =============================================================================
# Social Impact Engine - Population Risk and Nature-Based Solutions
# =============================================================================

import ee
from typing import Dict, Optional


def analyze_beneficiaries(lat: float, lon: float, buffer_km: float, flood_mask: Optional[ee.Image] = None) -> Dict:
    """
    Analyze population at risk from flooding using CIESIN GPW population data.
    
    Uses UN-adjusted population count dataset to estimate people and households
    in flood-prone areas.
    
    Args:
        lat: Latitude of location
        lon: Longitude of location
        buffer_km: Buffer radius in kilometers
        flood_mask: Optional EE Image with binary flood mask (1 = flooded, 0 = not flooded)
    
    Returns:
        Dictionary with people_at_risk and households_at_risk
    """
    try:
        # Create point geometry and buffer
        point = ee.Geometry.Point([lon, lat])
        buffer_m = buffer_km * 1000
        region = point.buffer(buffer_m)
        
        # Load CIESIN GPWv4.1 UN-adjusted population count
        # Get most recent year (2020)
        pop_collection = ee.ImageCollection("CIESIN/GPWv411/GPW_Population_Count")
        
        # Filter to most recent year and select population count band
        pop_image = pop_collection.filterDate('2020-01-01', '2020-12-31').first().select('population_count')
        
        # If flood mask provided, mask population to flooded areas only
        if flood_mask is not None:
            # Apply flood mask to population
            pop_at_risk = pop_image.updateMask(flood_mask)
        else:
            # Use full population in region
            pop_at_risk = pop_image
        
        # Calculate total population at risk
        # Reduce region to sum all population pixels
        pop_stats = pop_at_risk.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=1000,  # 1km resolution (GPW native resolution ~1km)
            maxPixels=1e9
        )
        
        # Get population count
        total_people = pop_stats.get('population_count').getInfo()
        
        # Handle None/null values
        if total_people is None:
            total_people = 0
        
        # Calculate households (global average: 4.9 people per household)
        avg_household_size = 4.9
        households_at_risk = int(total_people / avg_household_size)
        
        return {
            'people_at_risk': int(total_people),
            'households_at_risk': households_at_risk,
            'data_source': 'CIESIN GPWv4.11 (2020)',
            'buffer_km': buffer_km
        }
    
    except Exception as e:
        print(f"Error analyzing beneficiaries: {e}")
        return {
            'people_at_risk': 0,
            'households_at_risk': 0,
            'data_source': 'error',
            'error': str(e)
        }


def calculate_nature_value(intervention_type: str, area_hectares: float) -> Dict:
    """
    Calculate ecosystem services value for nature-based solutions.
    
    Focuses on carbon sequestration value for mangrove restoration.
    
    Args:
        intervention_type: Type of nature-based solution ('mangroves', 'wetlands', etc.)
        area_hectares: Area of intervention in hectares
    
    Returns:
        Dictionary with carbon sequestration metrics and value
    """
    # Carbon sequestration rates (tons CO2 per hectare per year)
    # Source: Global mangrove carbon sequestration studies
    MANGROVE_CARBON_RATE = 7.0  # tons CO2/ha/year
    
    # Carbon price (USD per ton CO2)
    # Source: Carbon credit market average
    CARBON_PRICE_USD = 70.0  # $/ton CO2
    
    if intervention_type.lower() == 'mangroves':
        # Calculate annual carbon sequestration
        carbon_tons_annual = area_hectares * MANGROVE_CARBON_RATE
        
        # Calculate economic value
        carbon_value_usd_annual = carbon_tons_annual * CARBON_PRICE_USD
        
        # Calculate 20-year cumulative value
        years = 20
        carbon_tons_cumulative = carbon_tons_annual * years
        carbon_value_cumulative = carbon_value_usd_annual * years
        
        return {
            'intervention_type': 'mangroves',
            'area_hectares': round(area_hectares, 2),
            'carbon_sequestration': {
                'annual_tons_co2': round(carbon_tons_annual, 2),
                'cumulative_tons_co2_20yr': round(carbon_tons_cumulative, 2),
                'rate_per_hectare': MANGROVE_CARBON_RATE
            },
            'economic_value': {
                'annual_usd': round(carbon_value_usd_annual, 2),
                'cumulative_usd_20yr': round(carbon_value_cumulative, 2),
                'carbon_price_per_ton': CARBON_PRICE_USD
            },
            'co_benefits': [
                'Storm surge protection',
                'Fish nursery habitat',
                'Water quality improvement',
                'Biodiversity conservation'
            ]
        }
    elif intervention_type.lower() == 'wetlands':
        # Wetlands also sequester carbon but at different rates
        WETLAND_CARBON_RATE = 5.0  # tons CO2/ha/year (lower than mangroves)
        
        carbon_tons_annual = area_hectares * WETLAND_CARBON_RATE
        carbon_value_usd_annual = carbon_tons_annual * CARBON_PRICE_USD
        
        years = 20
        carbon_tons_cumulative = carbon_tons_annual * years
        carbon_value_cumulative = carbon_value_usd_annual * years
        
        return {
            'intervention_type': 'wetlands',
            'area_hectares': round(area_hectares, 2),
            'carbon_sequestration': {
                'annual_tons_co2': round(carbon_tons_annual, 2),
                'cumulative_tons_co2_20yr': round(carbon_tons_cumulative, 2),
                'rate_per_hectare': WETLAND_CARBON_RATE
            },
            'economic_value': {
                'annual_usd': round(carbon_value_usd_annual, 2),
                'cumulative_usd_20yr': round(carbon_value_cumulative, 2),
                'carbon_price_per_ton': CARBON_PRICE_USD
            },
            'co_benefits': [
                'Flood water retention',
                'Groundwater recharge',
                'Wildlife habitat',
                'Recreation opportunities'
            ]
        }
    else:
        # Non-nature-based solution (e.g., sea wall, drainage)
        return {
            'intervention_type': intervention_type,
            'area_hectares': 0,
            'carbon_sequestration': {
                'annual_tons_co2': 0,
                'cumulative_tons_co2_20yr': 0,
                'rate_per_hectare': 0
            },
            'economic_value': {
                'annual_usd': 0,
                'cumulative_usd_20yr': 0,
                'carbon_price_per_ton': 0
            },
            'co_benefits': []
        }


def calculate_social_metrics(
    people_at_risk: int,
    households_at_risk: int,
    intervention_cost: float,
    nature_value: Optional[Dict] = None
) -> Dict:
    """
    Calculate social impact metrics and cost-effectiveness.
    
    Args:
        people_at_risk: Number of people benefiting from intervention
        households_at_risk: Number of households benefiting
        intervention_cost: Total project cost (CAPEX)
        nature_value: Optional nature-based solution value dict
    
    Returns:
        Dictionary with social impact metrics
    """
    # Calculate cost per beneficiary
    cost_per_person = intervention_cost / people_at_risk if people_at_risk > 0 else 0
    cost_per_household = intervention_cost / households_at_risk if households_at_risk > 0 else 0
    
    # Include nature value if available
    total_value = intervention_cost
    if nature_value and 'economic_value' in nature_value:
        carbon_value = nature_value['economic_value'].get('cumulative_usd_20yr', 0)
        total_value += carbon_value
    
    return {
        'beneficiaries': {
            'people_protected': people_at_risk,
            'households_protected': households_at_risk,
            'avg_household_size': 4.9
        },
        'cost_effectiveness': {
            'cost_per_person_protected': round(cost_per_person, 2),
            'cost_per_household_protected': round(cost_per_household, 2),
            'total_project_cost': intervention_cost
        },
        'social_value': {
            'lives_protected': people_at_risk,
            'displacement_avoided': households_at_risk,
            'community_resilience_improvement': 'High' if people_at_risk > 1000 else 'Medium'
        }
    }

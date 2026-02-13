# =============================================================================
# Flash Flood Risk Engine - Topographic Wetness Index (TWI) Model
# =============================================================================

import json
import os
import ee
import math
from gee_credentials import load_gee_credentials


def authenticate_gee():
    """
    Authenticate with Google Earth Engine using service account.
    
    Supports multiple credential sources (priority order):
    1. WARP_GEE_CREDENTIALS (Cloud Agents)
    2. GEE_SERVICE_ACCOUNT_JSON (legacy)
    3. credentials.json (project root)
    4. credentials.json (~/.adaptmetric/)
    """
    credentials_dict = load_gee_credentials()
    if not credentials_dict:
        raise ValueError(
            "Google Earth Engine credentials not found. "
            "Set WARP_GEE_CREDENTIALS or GEE_SERVICE_ACCOUNT_JSON env var, "
            "or place credentials.json in project root or ~/.adaptmetric/"
        )
    
    # Convert dict back to JSON string for ee.ServiceAccountCredentials
    credentials_json = json.dumps(credentials_dict)
    credentials = ee.ServiceAccountCredentials(
        credentials_dict['client_email'],
        key_data=credentials_json
    )
    ee.Initialize(credentials)


def analyze_flash_flood(lat: float, lon: float, rain_intensity_increase_pct: float) -> dict:
    """
    Analyze flash flood risk using Topographic Wetness Index (TWI) model.
    
    TWI = ln(flow_accumulation / tan(slope))
    Higher TWI values indicate areas prone to water accumulation and flooding.
    
    Args:
        lat: Latitude
        lon: Longitude
        rain_intensity_increase_pct: Percentage increase in rain intensity (e.g., 20 for +20%)
    
    Returns:
        Dictionary with:
        - 'baseline_flood_area_km2': Flood-prone area under baseline conditions
        - 'future_flood_area_km2': Flood-prone area under increased rainfall
        - 'risk_increase_pct': Percentage increase in flood risk
    """
    authenticate_gee()
    
    # Create 50km buffer around the point
    point = ee.Geometry.Point([lon, lat])
    buffer = point.buffer(50000)  # 50km in meters
    
    # Load NASA SRTM elevation data (90m resolution)
    elevation = ee.Image('USGS/SRTMGL1_003').select('elevation')
    
    # Calculate slope in degrees
    slope = ee.Terrain.slope(elevation)
    
    # Calculate flow accumulation using terrain analysis
    # Flow accumulation represents the number of upslope cells draining into each cell
    # Higher values indicate convergent flow patterns (valleys, channels)
    filled = elevation.focal_max(radius=90, units='meters', iterations=3)
    flow_direction = filled.subtract(elevation).gte(0)
    
    # Approximate flow accumulation using focal statistics
    # This is a simplified approach - ideally would use proper D8 flow algorithm
    flow_accumulation = elevation.focal_median(radius=500, units='meters')
    flow_accumulation = flow_accumulation.subtract(elevation).abs().add(1)
    
    # Calculate TWI (Topographic Wetness Index)
    # TWI = ln(flow_accumulation / tan(slope))
    # Add small constant to avoid division by zero
    slope_radians = slope.multiply(math.pi / 180)
    tan_slope = slope_radians.tan().add(0.001)
    
    # Normalize flow accumulation to reasonable range
    flow_acc_normalized = flow_accumulation.divide(100).add(1)
    
    # Calculate TWI
    twi = flow_acc_normalized.divide(tan_slope).log()
    
    # Baseline threshold for flooding (TWI > 12 indicates flood-prone areas)
    BASELINE_THRESHOLD = 12.0
    
    # Research-based scaling factor (7% reduction in threshold per % increase in rain)
    SCALING_FACTOR = 0.07
    
    # Calculate dynamic threshold based on rain intensity increase
    # As rain increases, threshold decreases, meaning more areas are flood-prone
    dynamic_threshold = BASELINE_THRESHOLD * (1 - (rain_intensity_increase_pct / 100 * SCALING_FACTOR))
    
    # Create flood masks
    baseline_flood_mask = twi.gte(BASELINE_THRESHOLD)
    future_flood_mask = twi.gte(dynamic_threshold)
    
    # Calculate pixel areas in square meters
    pixel_area = ee.Image.pixelArea()
    
    # Calculate baseline flood area
    baseline_flood_area_m2 = baseline_flood_mask.multiply(pixel_area).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=buffer,
        scale=500,  # 500m resolution for faster processing
        maxPixels=1e9
    ).get('elevation')
    
    # Calculate future flood area
    future_flood_area_m2 = future_flood_mask.multiply(pixel_area).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=buffer,
        scale=500,
        maxPixels=1e9
    ).get('elevation')
    
    # Convert to Python values
    baseline_flood_area_m2 = ee.Number(baseline_flood_area_m2).getInfo()
    future_flood_area_m2 = ee.Number(future_flood_area_m2).getInfo()
    
    # Handle None values
    if baseline_flood_area_m2 is None:
        baseline_flood_area_m2 = 0.0
    if future_flood_area_m2 is None:
        future_flood_area_m2 = 0.0
    
    # Convert from square meters to square kilometers
    baseline_flood_km2 = baseline_flood_area_m2 / 1_000_000
    future_flood_km2 = future_flood_area_m2 / 1_000_000
    
    # Calculate risk increase percentage
    if baseline_flood_km2 > 0:
        risk_increase_pct = ((future_flood_km2 - baseline_flood_km2) / baseline_flood_km2) * 100
    else:
        risk_increase_pct = 0.0
    
    return {
        'baseline_flood_area_km2': round(baseline_flood_km2, 2),
        'future_flood_area_km2': round(future_flood_km2, 2),
        'risk_increase_pct': round(risk_increase_pct, 2)
    }


def calculate_rainfall_frequency(intensity_increase_pct: float) -> dict:
    """
    Calculate rainfall frequency depths for different storm return periods.
    
    Uses research-based baseline rainfall depths and projects future depths
    based on intensity increase percentage.
    
    Args:
        intensity_increase_pct: Percentage increase in rainfall intensity (e.g., 10 for +10%)
    
    Returns:
        Dictionary with:
        - 'rain_chart_data': List of objects with period, baseline_mm, future_mm
    """
    # Baseline Rainfall Depths (from research - in millimeters)
    baseline_depths = {
        '1yr': 70.0,
        '10yr': 121.5,
        '50yr': 159.7,
        '100yr': 179.4
    }
    
    # Calculate future depths by applying intensity increase
    rain_chart_data = []
    
    for period, baseline_mm in baseline_depths.items():
        # Future depth = baseline * (1 + intensity_increase%)
        future_mm = baseline_mm * (1 + (intensity_increase_pct / 100))
        
        rain_chart_data.append({
            'period': period,
            'baseline_mm': round(baseline_mm, 2),
            'future_mm': round(future_mm, 2)
        })
    
    # Sort by severity (1yr, 10yr, 50yr, 100yr)
    # Define custom sort order
    period_order = {'1yr': 1, '10yr': 2, '50yr': 3, '100yr': 4}
    rain_chart_data.sort(key=lambda x: period_order.get(x['period'], 999))
    
    return {
        'rain_chart_data': rain_chart_data
    }


def analyze_infrastructure_risk(lat: float, lon: float, rain_intensity_pct: float) -> dict:
    """
    Analyze infrastructure flood risk using TWI-based flood mask and urban areas.
    
    Identifies built-up areas at risk of flash flooding based on topographic
    wetness index and rainfall intensity projections.
    
    Args:
        lat: Latitude
        lon: Longitude
        rain_intensity_pct: Percentage increase in rainfall intensity (e.g., 20 for +20%)
    
    Returns:
        Dictionary with:
        - 'infrastructure_risk': Dict containing total_km2, flooded_km2, risk_pct
    """
    authenticate_gee()
    
    # Create 50km buffer around the point
    point = ee.Geometry.Point([lon, lat])
    buffer = point.buffer(50000)  # 50km in meters
    
    # Load NASA SRTM elevation data (90m resolution)
    elevation = ee.Image('USGS/SRTMGL1_003').select('elevation')
    
    # Calculate slope in degrees
    slope = ee.Terrain.slope(elevation)
    
    # Calculate flow accumulation using terrain analysis
    filled = elevation.focal_max(radius=90, units='meters', iterations=3)
    flow_accumulation = elevation.focal_median(radius=500, units='meters')
    flow_accumulation = flow_accumulation.subtract(elevation).abs().add(1)
    
    # Calculate TWI (Topographic Wetness Index)
    slope_radians = slope.multiply(math.pi / 180)
    tan_slope = slope_radians.tan().add(0.001)
    flow_acc_normalized = flow_accumulation.divide(100).add(1)
    twi = flow_acc_normalized.divide(tan_slope).log()
    
    # Baseline threshold and scaling factor (from analyze_flash_flood)
    BASELINE_THRESHOLD = 12.0
    SCALING_FACTOR = 0.07
    
    # Calculate dynamic threshold based on rain intensity increase
    dynamic_threshold = BASELINE_THRESHOLD * (1 - (rain_intensity_pct / 100 * SCALING_FACTOR))
    
    # Create flood mask using TWI threshold
    flood_mask = twi.gte(dynamic_threshold)
    
    # Load ESA WorldCover 10m land cover dataset
    # Class 50 = Built-up
    land_cover = ee.ImageCollection('ESA/WorldCover/v200') \
        .first() \
        .select('Map')
    
    # Create built-up area mask (value 50 = Built-up)
    urban_mask = land_cover.eq(50)
    
    # Create intersection: urban areas that are flooded
    flooded_urban_mask = urban_mask.And(flood_mask)
    
    # Calculate pixel areas in square meters
    pixel_area = ee.Image.pixelArea()
    
    # Calculate total urban area
    total_urban_area_m2 = urban_mask.multiply(pixel_area).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=buffer,
        scale=100,  # 100m resolution for faster processing
        maxPixels=1e9
    ).get('Map')
    
    # Calculate flooded urban area
    flooded_urban_area_m2 = flooded_urban_mask.multiply(pixel_area).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=buffer,
        scale=100,
        maxPixels=1e9
    ).get('Map')
    
    # Convert to Python values
    total_urban_area_m2 = ee.Number(total_urban_area_m2).getInfo()
    flooded_urban_area_m2 = ee.Number(flooded_urban_area_m2).getInfo()
    
    # Handle None values (no urban area found)
    if total_urban_area_m2 is None:
        total_urban_area_m2 = 0.0
    if flooded_urban_area_m2 is None:
        flooded_urban_area_m2 = 0.0
    
    # Convert from square meters to square kilometers
    total_km2 = total_urban_area_m2 / 1_000_000
    flooded_km2 = flooded_urban_area_m2 / 1_000_000
    
    # Calculate risk percentage
    if total_km2 > 0:
        risk_pct = (flooded_km2 / total_km2) * 100
    else:
        risk_pct = 0.0
    
    return {
        'infrastructure_risk': {
            'total_km2': round(total_km2, 2),
            'flooded_km2': round(flooded_km2, 2),
            'risk_pct': round(risk_pct, 2)
        }
    }

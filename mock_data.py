"""
Mock Data Module for Testing
=============================

Provides realistic mock weather data for testing without hitting Google Earth Engine API.
Uses deterministic randomization based on lat/lon for reproducibility.

Usage:
    from mock_data import get_mock_weather
    
    weather = get_mock_weather(40.7, -74.0)
    print(weather['max_temp_celsius'])  # 19.8
"""

import hashlib
import math


def _get_seed_from_coords(lat: float, lon: float) -> int:
    """
    Generate a deterministic seed from coordinates.
    Same lat/lon always produces same seed for reproducibility.
    """
    # Create a unique string from coordinates
    coord_string = f"{lat:.6f},{lon:.6f}"
    # Hash it to get a consistent seed
    hash_object = hashlib.md5(coord_string.encode())
    # Convert first 8 bytes to integer
    return int.from_bytes(hash_object.digest()[:8], byteorder='big')


def _seeded_random(seed: int, min_val: float, max_val: float) -> float:
    """
    Generate a pseudo-random float in [min_val, max_val] using a seed.
    Uses simple LCG (Linear Congruential Generator) for determinism.
    """
    # LCG parameters (from Numerical Recipes)
    a = 1664525
    c = 1013904223
    m = 2**32
    
    # Generate next random value
    seed = (a * seed + c) % m
    
    # Normalize to [0, 1]
    normalized = seed / m
    
    # Scale to [min_val, max_val]
    return min_val + (normalized * (max_val - min_val))


def get_climate_zone(lat: float) -> str:
    """
    Determine climate zone based on latitude.
    
    Climate zones:
    - Tropical: 0-23.5° (hot, wet)
    - Subtropical: 23.5-35° (warm, variable)
    - Temperate: 35-50° (moderate, seasonal)
    - Cold: 50-66.5° (cool, dry)
    - Polar: 66.5-90° (cold, very dry)
    """
    abs_lat = abs(lat)
    
    if abs_lat < 23.5:
        return 'tropical'
    elif abs_lat < 35:
        return 'subtropical'
    elif abs_lat < 50:
        return 'temperate'
    elif abs_lat < 66.5:
        return 'cold'
    else:
        return 'polar'


def get_mock_weather(lat: float, lon: float) -> dict:
    """
    Generate realistic mock weather data based on geographic location.
    
    Uses climate zone classification and deterministic randomization
    to produce consistent, realistic weather data for testing.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
    
    Returns:
        Dictionary with weather data:
        - max_temp_celsius: Maximum temperature (°C)
        - total_precip_mm: Total precipitation (mm)
        - data_source: 'mock_data'
        - climate_zone: Climate zone classification
    
    Example:
        >>> weather = get_mock_weather(40.7, -74.0)  # New York
        >>> print(f"Temp: {weather['max_temp_celsius']}°C")
        >>> print(f"Rain: {weather['total_precip_mm']}mm")
    """
    # Validate inputs
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Longitude must be between -180 and 180, got {lon}")
    
    # Get deterministic seed from coordinates
    seed = _get_seed_from_coords(lat, lon)
    
    # Determine climate zone
    climate_zone = get_climate_zone(lat)
    
    # Define climate zone parameters (mean, variation)
    # Format: (temp_mean, temp_variation, rain_mean, rain_variation)
    climate_params = {
        'tropical': {
            'temp_mean': 28.0,
            'temp_variation': 3.0,     # ±3°C
            'rain_mean': 2000.0,
            'rain_variation': 800.0    # ±800mm
        },
        'subtropical': {
            'temp_mean': 24.0,
            'temp_variation': 4.0,     # ±4°C
            'rain_mean': 1000.0,
            'rain_variation': 500.0    # ±500mm
        },
        'temperate': {
            'temp_mean': 18.0,
            'temp_variation': 5.0,     # ±5°C
            'rain_mean': 700.0,
            'rain_variation': 400.0    # ±400mm
        },
        'cold': {
            'temp_mean': 10.0,
            'temp_variation': 6.0,     # ±6°C
            'rain_mean': 500.0,
            'rain_variation': 300.0    # ±300mm
        },
        'polar': {
            'temp_mean': -5.0,
            'temp_variation': 8.0,     # ±8°C
            'rain_mean': 200.0,
            'rain_variation': 150.0    # ±150mm
        }
    }
    
    params = climate_params[climate_zone]
    
    # Generate temperature with variation
    temp_min = params['temp_mean'] - params['temp_variation']
    temp_max = params['temp_mean'] + params['temp_variation']
    temperature = _seeded_random(seed, temp_min, temp_max)
    
    # Generate precipitation with variation
    # Use different seed offset for precipitation
    precip_seed = seed + 12345
    rain_min = max(0, params['rain_mean'] - params['rain_variation'])
    rain_max = params['rain_mean'] + params['rain_variation']
    precipitation = _seeded_random(precip_seed, rain_min, rain_max)
    
    # Apply coastal effect (more rain near coasts)
    # Coastal regions typically have 10-20% more precipitation
    # Use simple heuristic: longitude divisibility suggests coastal proximity
    is_coastal = (abs(lon) % 15 < 5) or (abs(lon) % 15 > 10)
    if is_coastal and climate_zone in ['tropical', 'subtropical', 'temperate']:
        precipitation *= 1.15  # 15% increase for coastal areas
    
    # Apply elevation proxy using latitude pattern
    # Higher latitudes in temperate zones tend to be cooler
    if climate_zone == 'temperate':
        abs_lat = abs(lat)
        if abs_lat > 45:
            temperature -= 2.0  # Mountain/highland adjustment
    
    # Round to realistic precision
    temperature = round(temperature, 1)
    precipitation = round(precipitation, 1)
    
    return {
        'max_temp_celsius': temperature,
        'total_precip_mm': precipitation,
        'data_source': 'mock_data',
        'climate_zone': climate_zone,
        'location': {
            'lat': lat,
            'lon': lon
        }
    }


def get_mock_coastal_params(lat: float, lon: float) -> dict:
    """
    Generate realistic mock coastal parameters for flood risk analysis.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
    
    Returns:
        Dictionary with coastal parameters:
        - slope_pct: Coastal slope percentage (0.1-20%)
        - max_wave_height: Storm wave height (0.5-6.0m)
        - data_source: 'mock_data'
    """
    # Validate inputs
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Longitude must be between -180 and 180, got {lon}")
    
    seed = _get_seed_from_coords(lat, lon)
    
    # Coastal slope varies by geography
    # Steep: Pacific Ring of Fire, rocky coasts (10-20%)
    # Moderate: Mixed coastlines (2-10%)
    # Gentle: Atlantic plains, deltas (0.1-2%)
    
    # Use latitude and longitude to determine typical slope
    abs_lat = abs(lat)
    
    if abs_lat < 10:
        # Tropical deltas - very gentle slopes
        slope_min, slope_max = 0.1, 2.0
    elif abs_lat < 35:
        # Subtropical - moderate slopes
        slope_min, slope_max = 2.0, 8.0
    else:
        # Temperate/cold - steeper coastlines
        slope_min, slope_max = 5.0, 15.0
    
    slope_pct = _seeded_random(seed, slope_min, slope_max)
    
    # Wave height depends on exposure and latitude
    # Higher latitudes = stronger storms
    # Use different seed offset
    wave_seed = seed + 54321
    
    # Storm wave heights vary by location
    if abs_lat < 15:
        # Tropical cyclone zones
        wave_min, wave_max = 1.5, 5.0
    elif abs_lat < 40:
        # Subtropical storm zones
        wave_min, wave_max = 1.0, 4.0
    else:
        # Temperate/polar - North Atlantic/Pacific storms
        wave_min, wave_max = 2.0, 6.0
    
    wave_height = _seeded_random(wave_seed, wave_min, wave_max)
    
    return {
        'slope_pct': round(slope_pct, 2),
        'max_wave_height': round(wave_height, 2),
        'data_source': 'mock_data',
        'location': {
            'lat': lat,
            'lon': lon
        }
    }


def get_mock_elevation(lat: float, lon: float) -> float:
    """
    Generate realistic mock elevation data.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
    
    Returns:
        Elevation in meters above sea level
    """
    # Validate inputs
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Longitude must be between -180 and 180, got {lon}")
    
    seed = _get_seed_from_coords(lat, lon)
    abs_lat = abs(lat)
    
    # Elevation patterns by region
    if abs_lat < 10:
        # Tropical lowlands
        elev_min, elev_max = 0, 200
    elif abs_lat < 30:
        # Subtropical - variable (includes deserts and highlands)
        elev_min, elev_max = 0, 800
    elif abs_lat < 50:
        # Temperate - more variable (includes mountain ranges)
        elev_min, elev_max = 0, 1500
    else:
        # High latitudes - generally lower
        elev_min, elev_max = 0, 500
    
    # Add longitude-based variation (simple mountain range proxy)
    # Every 30° of longitude, simulate a mountain range
    lon_cycle = abs(lon) % 30
    if 10 < lon_cycle < 20:
        # In a "mountain range" zone
        elev_max *= 2
    
    elevation = _seeded_random(seed + 99999, elev_min, elev_max)
    
    return round(elevation, 1)


def get_mock_monthly_data(lat: float, lon: float) -> dict:
    """
    Generate realistic mock monthly climate data.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
    
    Returns:
        Dictionary with monthly data:
        - rainfall_monthly_mm: List of 12 monthly rainfall values
        - soil_moisture_monthly: List of 12 monthly soil moisture values (0-1)
        - temp_monthly_celsius: List of 12 monthly temperature values
    """
    # Validate inputs
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Longitude must be between -180 and 180, got {lon}")
    
    seed = _get_seed_from_coords(lat, lon)
    climate_zone = get_climate_zone(lat)
    
    # Get annual values
    annual_weather = get_mock_weather(lat, lon)
    annual_temp = annual_weather['max_temp_celsius']
    annual_rain = annual_weather['total_precip_mm']
    
    # Determine hemisphere (affects seasonal patterns)
    is_northern = lat >= 0
    
    rainfall_monthly = []
    soil_moisture_monthly = []
    temp_monthly = []
    
    for month in range(12):
        # Seasonal variation based on hemisphere
        if is_northern:
            # Northern hemisphere: warm in Jun-Aug, cold in Dec-Feb
            season_factor = math.sin((month - 3) * math.pi / 6)
        else:
            # Southern hemisphere: opposite
            season_factor = math.sin((month - 9) * math.pi / 6)
        
        # Temperature variation
        if climate_zone == 'tropical':
            temp_variation = 3.0  # Minimal seasonal variation
        elif climate_zone == 'subtropical':
            temp_variation = 8.0
        elif climate_zone == 'temperate':
            temp_variation = 15.0
        elif climate_zone == 'cold':
            temp_variation = 20.0
        else:  # polar
            temp_variation = 25.0
        
        month_temp = annual_temp + (season_factor * temp_variation / 2)
        temp_monthly.append(round(month_temp, 1))
        
        # Rainfall variation (tropical has wet/dry seasons)
        if climate_zone == 'tropical':
            # Monsoon pattern - most rain in summer
            rain_factor = max(0, season_factor)
            month_rain = (annual_rain / 12) * (1 + rain_factor)
        elif climate_zone in ['subtropical', 'temperate']:
            # More even distribution with slight winter peak
            rain_factor = -season_factor * 0.3  # Winter slightly wetter
            month_rain = (annual_rain / 12) * (1 + rain_factor)
        else:
            # Cold/polar - very even (low) precipitation
            month_rain = annual_rain / 12
        
        # Add some randomness to monthly rain
        month_seed = seed + month * 1000
        rain_noise = _seeded_random(month_seed, 0.8, 1.2)
        month_rain *= rain_noise
        
        rainfall_monthly.append(round(month_rain, 1))
        
        # Soil moisture correlates with rainfall and temperature
        # Higher rain = higher moisture
        # Higher temp = lower moisture (evaporation)
        rain_contribution = min(month_rain / 150.0, 1.0)  # Cap at 150mm
        temp_penalty = max(0, (month_temp - 20) / 50.0)   # Penalty above 20°C
        soil_moisture = min(1.0, max(0.1, rain_contribution - temp_penalty * 0.3))
        
        soil_moisture_monthly.append(round(soil_moisture, 4))
    
    return {
        'rainfall_monthly_mm': rainfall_monthly,
        'soil_moisture_monthly': soil_moisture_monthly,
        'temp_monthly_celsius': temp_monthly,
        'data_source': 'mock_data',
        'location': {
            'lat': lat,
            'lon': lon
        }
    }


# Example usage and testing
if __name__ == '__main__':
    print("=== Mock Data Module Test ===\n")
    
    # Test locations
    test_locations = [
        (40.7, -74.0, "New York City"),
        (-2.5, 28.8, "Central Africa (Tropical)"),
        (13.5, 2.1, "West Africa (Sahel)"),
        (51.5, -0.1, "London"),
        (-33.9, 18.4, "Cape Town"),
        (35.7, 139.7, "Tokyo"),
        (70.0, -45.0, "Greenland (Polar)")
    ]
    
    print("1. Weather Data Test:")
    print("-" * 80)
    for lat, lon, name in test_locations:
        weather = get_mock_weather(lat, lon)
        print(f"{name:30s} | Temp: {weather['max_temp_celsius']:5.1f}°C | "
              f"Rain: {weather['total_precip_mm']:6.1f}mm | "
              f"Zone: {weather['climate_zone']}")
    
    print("\n2. Coastal Parameters Test:")
    print("-" * 80)
    for lat, lon, name in test_locations[:4]:
        coastal = get_mock_coastal_params(lat, lon)
        print(f"{name:30s} | Slope: {coastal['slope_pct']:5.2f}% | "
              f"Wave: {coastal['max_wave_height']:4.2f}m")
    
    print("\n3. Reproducibility Test (same location called twice):")
    print("-" * 80)
    loc = test_locations[0]
    weather1 = get_mock_weather(loc[0], loc[1])
    weather2 = get_mock_weather(loc[0], loc[1])
    print(f"Call 1: Temp={weather1['max_temp_celsius']}°C, Rain={weather1['total_precip_mm']}mm")
    print(f"Call 2: Temp={weather2['max_temp_celsius']}°C, Rain={weather2['total_precip_mm']}mm")
    print(f"Match: {weather1 == weather2}")
    
    print("\n4. Monthly Data Test (New York):")
    print("-" * 80)
    monthly = get_mock_monthly_data(40.7, -74.0)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    print("Month  | Temp (°C) | Rain (mm) | Soil Moisture")
    print("-" * 50)
    for i, month in enumerate(months):
        print(f"{month:6s} | {monthly['temp_monthly_celsius'][i]:9.1f} | "
              f"{monthly['rainfall_monthly_mm'][i]:9.1f} | "
              f"{monthly['soil_moisture_monthly'][i]:13.4f}")
    
    print("\n=== All tests complete! ===")

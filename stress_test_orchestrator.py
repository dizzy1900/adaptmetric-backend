#!/usr/bin/env python3
"""Monte Carlo Stress Test Orchestrator for Global Risk Atlas.

Loads global_atlas_v2.json and runs Monte Carlo simulations (50 iterations)
for all 100 locations in parallel. Appends monte_carlo_analysis to each location.

OUTPUT FORMAT: Pure JSON Array (no wrapper objects).
"""

import json
import math
import random
import statistics
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Monte Carlo configuration
MC_ITERATIONS = 50
RANDOM_SEED = 42  # For reproducibility

# Parameter variation ranges (as percentage of base value or absolute deltas)
TEMP_VARIATION_C = 1.5  # +/- degrees Celsius
RAIN_VARIATION_PCT = 20.0  # +/- percentage of base rainfall
SLR_VARIATION_M = 0.3  # +/- meters for sea level rise
RAIN_INTENSITY_VARIATION_PCT = 15.0  # +/- percentage for flood intensity


@dataclass
class MonteCarloResult:
    """Results from Monte Carlo simulation for a single metric."""
    mean: float
    std: float
    min: float
    max: float
    p5: float
    p25: float
    p50: float  # median
    p75: float
    p95: float
    samples: List[float]


def percentile(data: List[float], p: float) -> float:
    """Calculate the p-th percentile of a list of numbers."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    d0 = sorted_data[int(f)] * (c - k)
    d1 = sorted_data[int(c)] * (k - f)
    return d0 + d1


def compute_mc_stats(samples: List[float]) -> Dict[str, Any]:
    """Compute Monte Carlo statistics from samples."""
    if not samples:
        return {
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "p5": 0.0,
            "p25": 0.0,
            "p50": 0.0,
            "p75": 0.0,
            "p95": 0.0,
        }
    
    return {
        "mean": round(statistics.mean(samples), 4),
        "std": round(statistics.stdev(samples) if len(samples) > 1 else 0.0, 4),
        "min": round(min(samples), 4),
        "max": round(max(samples), 4),
        "p5": round(percentile(samples, 5), 4),
        "p25": round(percentile(samples, 25), 4),
        "p50": round(percentile(samples, 50), 4),
        "p75": round(percentile(samples, 75), 4),
        "p95": round(percentile(samples, 95), 4),
    }


def simulate_agriculture_iteration(
    base_temp: float,
    base_rain: float,
    crop_type: str,
    rng: random.Random
) -> Dict[str, float]:
    """Run one Monte Carlo iteration for agriculture analysis."""
    # Vary temperature and rainfall
    temp_delta = rng.uniform(-TEMP_VARIATION_C, TEMP_VARIATION_C)
    rain_delta_pct = rng.uniform(-RAIN_VARIATION_PCT, RAIN_VARIATION_PCT)
    
    sim_temp = base_temp + temp_delta
    sim_rain = base_rain * (1 + rain_delta_pct / 100.0)
    
    # Simplified yield model (mirrors physics_engine logic)
    # Temperature stress
    optimal_temps = {
        'maize': (20.0, 30.0),
        'rice': (22.0, 32.0),
        'wheat': (15.0, 25.0),
        'soy': (20.0, 30.0),
        'cocoa': (21.0, 32.0),
    }
    t_min, t_max = optimal_temps.get(crop_type, (20.0, 30.0))
    
    if sim_temp < t_min:
        temp_stress = max(0.0, 1.0 - (t_min - sim_temp) * 0.05)
    elif sim_temp > t_max:
        temp_stress = max(0.0, 1.0 - (sim_temp - t_max) * 0.08)
    else:
        temp_stress = 1.0
    
    # Rainfall stress
    optimal_rain = {'maize': 800, 'rice': 1500, 'wheat': 600, 'soy': 700, 'cocoa': 1800}
    opt_rain = optimal_rain.get(crop_type, 800)
    rain_ratio = sim_rain / opt_rain if opt_rain > 0 else 1.0
    
    if rain_ratio < 0.5:
        rain_stress = 0.3 + rain_ratio * 0.8
    elif rain_ratio > 2.0:
        rain_stress = max(0.4, 1.0 - (rain_ratio - 2.0) * 0.15)
    else:
        rain_stress = min(1.0, 0.7 + rain_ratio * 0.3)
    
    # Combined yield (as percentage of optimal)
    standard_yield = temp_stress * rain_stress * 100.0
    
    # Resilient seeds provide 15-30% buffer
    resilient_boost = rng.uniform(0.15, 0.30)
    resilient_yield = min(100.0, standard_yield * (1 + resilient_boost))
    
    avoided_loss = resilient_yield - standard_yield
    
    # Simplified NPV calculation
    price_per_ton = {'maize': 4800, 'rice': 4000, 'wheat': 3500, 'soy': 5000, 'cocoa': 2500}
    price = price_per_ton.get(crop_type, 4000)
    
    # NPV approximation based on yield improvement
    base_npv = (resilient_yield / 100.0) * price * 10  # 10 year horizon approximation
    npv = base_npv * rng.uniform(0.85, 1.15)  # Add market uncertainty
    
    return {
        "standard_yield_pct": standard_yield,
        "resilient_yield_pct": resilient_yield,
        "avoided_loss_pct": avoided_loss,
        "npv_usd": npv,
        "sim_temp_c": sim_temp,
        "sim_rain_mm": sim_rain,
    }


def simulate_coastal_iteration(
    lat: float,
    lon: float,
    base_slr: float,
    rng: random.Random
) -> Dict[str, float]:
    """Run one Monte Carlo iteration for coastal analysis."""
    # Vary SLR projection
    slr_delta = rng.uniform(-SLR_VARIATION_M, SLR_VARIATION_M)
    sim_slr = max(0.0, base_slr + slr_delta)
    
    # Storm surge varies with SLR scenarios
    surge_m = rng.uniform(1.5, 4.0) if sim_slr > 0.5 else rng.uniform(0.5, 2.0)
    
    total_water_level = sim_slr + surge_m
    
    # Pseudo-elevation (deterministic by location for consistency)
    seed = int((abs(lat) * 1000.0) + (abs(lon) * 1000.0)) % 1000
    base_elevation = 1.0 + (seed / 1000.0) * 4.0
    # Add small random variation
    elevation = base_elevation + rng.uniform(-0.3, 0.3)
    
    flood_depth = max(0.0, total_water_level - elevation)
    
    # Risk score (0-100)
    if flood_depth <= 0:
        risk_score = rng.uniform(5, 20)
    elif flood_depth < 0.5:
        risk_score = rng.uniform(20, 45)
    elif flood_depth < 1.5:
        risk_score = rng.uniform(45, 75)
    else:
        risk_score = rng.uniform(75, 100)
    
    # Economic exposure (simplified)
    exposure_usd = flood_depth * rng.uniform(50_000_000, 200_000_000)
    
    return {
        "flood_depth_m": flood_depth,
        "risk_score": risk_score,
        "total_water_level_m": total_water_level,
        "economic_exposure_usd": exposure_usd,
        "sim_slr_m": sim_slr,
    }


def simulate_flood_iteration(
    lat: float,
    lon: float,
    base_rain_intensity: float,
    rng: random.Random
) -> Dict[str, float]:
    """Run one Monte Carlo iteration for flood analysis."""
    # Vary rain intensity increase
    intensity_delta = rng.uniform(-RAIN_INTENSITY_VARIATION_PCT, RAIN_INTENSITY_VARIATION_PCT)
    sim_intensity = max(0.0, base_rain_intensity + intensity_delta)
    
    # Baseline flood area (deterministic by location)
    seed = int((abs(lat) * 100.0) + (abs(lon) * 10.0)) % 100
    baseline_area = 50.0 + seed
    
    # Future area scales with intensity
    scale = 1.0 + sim_intensity * 0.02
    future_area = baseline_area * scale * rng.uniform(0.9, 1.1)
    
    risk_increase_pct = ((future_area - baseline_area) / baseline_area) * 100.0
    
    # Population at risk (simplified model)
    pop_density = rng.uniform(1000, 15000)  # people per km2
    population_at_risk = future_area * pop_density
    
    # Value protected with adaptation
    adaptation_efficacy = rng.uniform(0.4, 0.7)
    value_protected_usd = population_at_risk * rng.uniform(5000, 15000) * adaptation_efficacy
    
    return {
        "future_flood_area_km2": future_area,
        "risk_increase_pct": risk_increase_pct,
        "population_at_risk": population_at_risk,
        "value_protected_usd": value_protected_usd,
        "sim_rain_intensity_pct": sim_intensity,
    }


def run_monte_carlo_for_location(location: Dict[str, Any], loc_index: int) -> Dict[str, Any]:
    """Run Monte Carlo simulation for a single location.
    
    Args:
        location: The location data from global_atlas_v2.json
        loc_index: Index for seeding RNG (ensures reproducibility)
    
    Returns:
        The location dict with monte_carlo_analysis appended
    """
    # Create seeded RNG for this location
    rng = random.Random(RANDOM_SEED + loc_index)
    
    project_type = location.get("project_type", "unknown")
    lat = location.get("location", {}).get("lat", 0.0)
    lon = location.get("location", {}).get("lon", 0.0)
    
    mc_results = {
        "iterations": MC_ITERATIONS,
        "random_seed": RANDOM_SEED + loc_index,
    }
    
    if project_type == "agriculture":
        # Get base conditions
        climate = location.get("climate_conditions", {})
        base_temp = climate.get("temperature_c", 25.0)
        base_rain = climate.get("rainfall_mm", 1000.0)
        crop_type = location.get("crop_analysis", {}).get("crop_type", "maize")
        
        # Run iterations
        samples = {
            "standard_yield_pct": [],
            "resilient_yield_pct": [],
            "avoided_loss_pct": [],
            "npv_usd": [],
        }
        
        for _ in range(MC_ITERATIONS):
            result = simulate_agriculture_iteration(base_temp, base_rain, crop_type, rng)
            for key in samples:
                samples[key].append(result[key])
        
        mc_results["metrics"] = {
            "standard_yield_pct": compute_mc_stats(samples["standard_yield_pct"]),
            "resilient_yield_pct": compute_mc_stats(samples["resilient_yield_pct"]),
            "avoided_loss_pct": compute_mc_stats(samples["avoided_loss_pct"]),
            "npv_usd": compute_mc_stats(samples["npv_usd"]),
        }
        mc_results["parameter_ranges"] = {
            "temp_variation_c": TEMP_VARIATION_C,
            "rain_variation_pct": RAIN_VARIATION_PCT,
        }
        
    elif project_type == "coastal":
        # Get base conditions
        input_cond = location.get("input_conditions", {})
        base_slr = input_cond.get("slr_projection_m", 1.0)
        
        samples = {
            "flood_depth_m": [],
            "risk_score": [],
            "total_water_level_m": [],
            "economic_exposure_usd": [],
        }
        
        for _ in range(MC_ITERATIONS):
            result = simulate_coastal_iteration(lat, lon, base_slr, rng)
            for key in samples:
                samples[key].append(result[key])
        
        mc_results["metrics"] = {
            "flood_depth_m": compute_mc_stats(samples["flood_depth_m"]),
            "risk_score": compute_mc_stats(samples["risk_score"]),
            "total_water_level_m": compute_mc_stats(samples["total_water_level_m"]),
            "economic_exposure_usd": compute_mc_stats(samples["economic_exposure_usd"]),
        }
        mc_results["parameter_ranges"] = {
            "slr_variation_m": SLR_VARIATION_M,
            "surge_range_m": "1.5-4.0 (high SLR) / 0.5-2.0 (low SLR)",
        }
        
    elif project_type == "flood":
        # Get base conditions
        input_cond = location.get("input_conditions", {})
        base_intensity = input_cond.get("rain_intensity_increase_pct", 25.0)
        
        samples = {
            "future_flood_area_km2": [],
            "risk_increase_pct": [],
            "population_at_risk": [],
            "value_protected_usd": [],
        }
        
        for _ in range(MC_ITERATIONS):
            result = simulate_flood_iteration(lat, lon, base_intensity, rng)
            for key in samples:
                samples[key].append(result[key])
        
        mc_results["metrics"] = {
            "future_flood_area_km2": compute_mc_stats(samples["future_flood_area_km2"]),
            "risk_increase_pct": compute_mc_stats(samples["risk_increase_pct"]),
            "population_at_risk": compute_mc_stats(samples["population_at_risk"]),
            "value_protected_usd": compute_mc_stats(samples["value_protected_usd"]),
        }
        mc_results["parameter_ranges"] = {
            "rain_intensity_variation_pct": RAIN_INTENSITY_VARIATION_PCT,
        }
    
    else:
        mc_results["error"] = f"Unknown project type: {project_type}"
    
    # Create a new dict with monte_carlo_analysis appended
    result = dict(location)
    result["monte_carlo_analysis"] = mc_results
    
    return result


def process_location_wrapper(args):
    """Wrapper for multiprocessing - unpacks tuple args."""
    location, idx = args
    return run_monte_carlo_for_location(location, idx)


def main():
    """Main entry point - load atlas, run MC, save results."""
    repo_root = Path(__file__).resolve().parent
    input_file = repo_root / "global_atlas_v2.json"
    output_file = repo_root / "final_100_risk_atlas.json"
    
    print(f"Loading {input_file}...")
    with input_file.open("r", encoding="utf-8") as f:
        locations = json.load(f)
    
    print(f"Loaded {len(locations)} locations")
    print(f"Running Monte Carlo simulation ({MC_ITERATIONS} iterations per location)...")
    
    # Prepare arguments for parallel processing
    args_list = [(loc, idx) for idx, loc in enumerate(locations)]
    
    # Run in parallel
    results = []
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(process_location_wrapper, args): args[1] for args in args_list}
        
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1
            if completed % 20 == 0 or completed == len(locations):
                print(f"  Completed {completed}/{len(locations)} locations")
    
    # Sort results by project_type then name for consistency
    results.sort(key=lambda r: (
        r.get("target", {}).get("project_type", ""),
        r.get("target", {}).get("name", "")
    ))
    
    # CRITICAL: Output as pure JSON array (no wrapper)
    print(f"Writing results to {output_file}...")
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        f.write("\n")  # Trailing newline
    
    # Summary stats
    project_types = {}
    for r in results:
        pt = r.get("project_type", "unknown")
        project_types[pt] = project_types.get(pt, 0) + 1
    
    print(f"\nCompleted Monte Carlo stress test for {len(results)} locations:")
    for pt, count in sorted(project_types.items()):
        print(f"  - {pt}: {count}")
    print(f"\nOutput saved to: {output_file}")
    print("Output format: Pure JSON Array (frontend compatible)")


if __name__ == "__main__":
    main()

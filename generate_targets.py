#!/usr/bin/env python3
"""Generate global_targets_100.csv with 100 diverse global locations.

Categories (25 each):
- Global Ports (project_type='coastal')
- Maize Hubs (project_type='agriculture', crop_type='maize')
- Rice Hubs (project_type='agriculture', crop_type='rice')
- Vulnerable Coastal Cities (project_type='flood')
"""

import csv
from pathlib import Path


# 25 Global Ports - Major shipping hubs worldwide
GLOBAL_PORTS = [
    ("Shanghai Port", 31.2304, 121.4737),
    ("Singapore Port", 1.2644, 103.8220),
    ("Rotterdam Port", 51.9054, 4.4661),
    ("Los Angeles Port", 33.7406, -118.2712),
    ("Jebel Ali Port", 24.9857, 55.0579),
    ("Hamburg Port", 53.5454, 9.9666),
    ("Antwerp Port", 51.2577, 4.4119),
    ("Busan Port", 35.1028, 129.0403),
    ("Hong Kong Port", 22.2855, 114.1577),
    ("Ningbo-Zhoushan Port", 29.8683, 121.5440),
    ("Qingdao Port", 36.0671, 120.3826),
    ("Guangzhou Port", 23.0989, 113.3191),
    ("Dubai Port", 25.2697, 55.3095),
    ("Tianjin Port", 38.9860, 117.7856),
    ("Port Klang", 3.0017, 101.3827),
    ("Kaohsiung Port", 22.6124, 120.2850),
    ("Dalian Port", 38.9140, 121.6147),
    ("Xiamen Port", 24.4797, 118.0819),
    ("Tanjung Pelepas Port", 1.3633, 103.5460),
    ("Laem Chabang Port", 13.0670, 100.8827),
    ("Santos Port", -23.9536, -46.3336),
    ("Colombo Port", 6.9344, 79.8428),
    ("Piraeus Port", 37.9443, 23.6418),
    ("Valencia Port", 39.4447, -0.3263),
    ("Felixstowe Port", 51.9526, 1.3136),
]

# 25 Maize Hubs - Key corn belt regions worldwide
MAIZE_HUBS = [
    ("Iowa Corn Belt", 42.0046, -93.2140),
    ("Illinois Corn Belt", 40.6331, -89.3985),
    ("Nebraska Corn Belt", 41.1254, -98.2681),
    ("Mato Grosso Brazil", -12.6819, -56.9211),
    ("Goias Brazil", -15.8270, -49.8362),
    ("Parana Brazil", -24.0245, -51.2963),
    ("Heilongjiang China", 46.8018, 127.0769),
    ("Jilin China", 43.8370, 126.5496),
    ("Shandong China", 36.6683, 117.0204),
    ("Henan China", 34.7657, 113.7536),
    ("Poltava Ukraine", 49.5883, 34.5514),
    ("Cherkasy Ukraine", 49.4444, 32.0598),
    ("Cordoba Argentina", -31.4201, -64.1888),
    ("Santa Fe Argentina", -31.6107, -60.6973),
    ("Buenos Aires Province", -36.6769, -60.5588),
    ("Punjab India", 30.7333, 76.7794),
    ("Madhya Pradesh India", 23.2599, 77.4126),
    ("Karnataka India", 15.3173, 75.7139),
    ("Free State South Africa", -28.4541, 26.7968),
    ("Mpumalanga South Africa", -25.4651, 30.9853),
    ("Rift Valley Kenya", -0.3031, 36.0800),
    ("Central Mexico", 19.4326, -99.1332),
    ("Jalisco Mexico", 20.6595, -103.3494),
    ("Sinaloa Mexico", 24.8091, -107.3940),
    ("Northern France", 49.8941, 2.2958),
]

# 25 Rice Hubs - Major rice basket regions
RICE_HUBS = [
    ("Mekong Delta Vietnam", 10.0452, 105.7469),
    ("Red River Delta Vietnam", 20.8449, 106.6881),
    ("Central Thailand", 14.5995, 100.5967),
    ("Isan Thailand", 15.2294, 104.8574),
    ("West Bengal India", 22.9868, 87.8550),
    ("Uttar Pradesh India", 26.8467, 80.9462),
    ("Punjab India Rice", 31.1471, 75.3412),
    ("Andhra Pradesh India", 15.9129, 79.7400),
    ("Tamil Nadu India", 11.1271, 78.6569),
    ("Ganges Basin Bangladesh", 23.6850, 90.3563),
    ("Sylhet Bangladesh", 24.8949, 91.8687),
    ("Jiangxi China", 28.6820, 115.8579),
    ("Hunan China", 27.6104, 111.7088),
    ("Hubei China", 30.9756, 112.2707),
    ("Guangxi China", 23.7248, 108.8076),
    ("Anhui China", 31.8612, 117.2840),
    ("Arkansas USA", 34.7465, -92.2896),
    ("Louisiana USA", 30.9843, -91.9623),
    ("California Sacramento", 38.5816, -121.4944),
    ("Java Indonesia", -7.1500, 110.4200),
    ("Sulawesi Indonesia", -1.4300, 121.4456),
    ("Luzon Philippines", 15.4826, 120.5959),
    ("Ayeyarwady Myanmar", 16.7833, 95.1833),
    ("Khyber Pakhtunkhwa Pakistan", 34.0151, 71.5249),
    ("Sindh Pakistan", 25.8943, 68.5247),
]

# 25 Vulnerable Coastal Cities - High flood risk
VULNERABLE_COASTAL_CITIES = [
    ("Miami", 25.7617, -80.1918),
    ("Osaka", 34.6937, 135.5023),
    ("Alexandria", 31.2001, 29.9187),
    ("Dhaka", 23.8103, 90.4125),
    ("Venice", 45.4408, 12.3155),
    ("Lagos", 6.5244, 3.3792),
    ("Jakarta", -6.2088, 106.8456),
    ("Bangkok", 13.7563, 100.5018),
    ("Ho Chi Minh City", 10.8231, 106.6297),
    ("Manila", 14.5995, 120.9842),
    ("Mumbai", 19.0760, 72.8777),
    ("Kolkata", 22.5726, 88.3639),
    ("Shanghai", 31.2304, 121.4737),
    ("Guangzhou", 23.1291, 113.2644),
    ("Shenzhen", 22.5431, 114.0579),
    ("New Orleans", 29.9511, -90.0715),
    ("Houston", 29.7604, -95.3698),
    ("Tokyo", 35.6762, 139.6503),
    ("Tianjin", 39.3434, 117.3616),
    ("Chittagong", 22.3569, 91.7832),
    ("Hai Phong", 20.8449, 106.6881),
    ("Surabaya", -7.2504, 112.7688),
    ("Chennai", 13.0827, 80.2707),
    ("Karachi", 24.8607, 67.0011),
    ("Abidjan", 5.3600, -4.0083),
]


def main():
    """Generate CSV with all 100 targets."""
    repo_root = Path(__file__).resolve().parent
    output_path = repo_root / "global_targets_100.csv"

    rows = []

    # Add Global Ports (coastal)
    for name, lat, lon in GLOBAL_PORTS:
        rows.append({
            "name": name,
            "lat": lat,
            "lon": lon,
            "project_type": "coastal",
            "crop_type": "",
        })

    # Add Maize Hubs (agriculture)
    for name, lat, lon in MAIZE_HUBS:
        rows.append({
            "name": name,
            "lat": lat,
            "lon": lon,
            "project_type": "agriculture",
            "crop_type": "maize",
        })

    # Add Rice Hubs (agriculture)
    for name, lat, lon in RICE_HUBS:
        rows.append({
            "name": name,
            "lat": lat,
            "lon": lon,
            "project_type": "agriculture",
            "crop_type": "rice",
        })

    # Add Vulnerable Coastal Cities (flood)
    for name, lat, lon in VULNERABLE_COASTAL_CITIES:
        rows.append({
            "name": name,
            "lat": lat,
            "lon": lon,
            "project_type": "flood",
            "crop_type": "",
        })

    # Write CSV
    fieldnames = ["name", "lat", "lon", "project_type", "crop_type"]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} targets in {output_path}")

    # Verify counts
    coastal_count = sum(1 for r in rows if r["project_type"] == "coastal")
    maize_count = sum(1 for r in rows if r["crop_type"] == "maize")
    rice_count = sum(1 for r in rows if r["crop_type"] == "rice")
    flood_count = sum(1 for r in rows if r["project_type"] == "flood")

    print(f"  - Coastal (ports): {coastal_count}")
    print(f"  - Agriculture (maize): {maize_count}")
    print(f"  - Agriculture (rice): {rice_count}")
    print(f"  - Flood (vulnerable cities): {flood_count}")


if __name__ == "__main__":
    main()

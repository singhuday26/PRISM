"""Seed MongoDB with realistic simulated ecosystem institutions.

Run:  python -m backend.scripts.seed_ecosystem
"""
from __future__ import annotations

import random
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_db  # noqa: E402

random.seed(42)

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

REGIONS = [
    "IN-MH", "IN-KA", "IN-KL", "IN-TN", "IN-DL",
    "IN-GJ", "IN-RJ", "IN-UP", "IN-WB", "IN-AP",
    "IN-TS", "IN-BR", "IN-MP", "IN-HR", "IN-PB",
    "IN-GA", "IN-JH", "IN-OR", "IN-CG", "IN-AR",
]

REGION_CITIES = {
    "IN-MH": ["Mumbai", "Pune", "Nagpur"],
    "IN-KA": ["Bengaluru", "Mysuru", "Hubli"],
    "IN-KL": ["Kochi", "Thiruvananthapuram", "Kozhikode"],
    "IN-TN": ["Chennai", "Coimbatore", "Madurai"],
    "IN-DL": ["New Delhi", "Dwarka", "Saket"],
    "IN-GJ": ["Ahmedabad", "Surat", "Vadodara"],
    "IN-RJ": ["Jaipur", "Jodhpur", "Udaipur"],
    "IN-UP": ["Lucknow", "Kanpur", "Varanasi"],
    "IN-WB": ["Kolkata", "Howrah", "Siliguri"],
    "IN-AP": ["Visakhapatnam", "Vijayawada", "Tirupati"],
    "IN-TS": ["Hyderabad", "Warangal", "Nizamabad"],
    "IN-BR": ["Patna", "Gaya", "Muzaffarpur"],
    "IN-MP": ["Bhopal", "Indore", "Jabalpur"],
    "IN-HR": ["Gurugram", "Faridabad", "Karnal"],
    "IN-PB": ["Chandigarh", "Ludhiana", "Amritsar"],
    "IN-GA": ["Panaji", "Margao"],
    "IN-JH": ["Ranchi", "Jamshedpur", "Dhanbad"],
    "IN-OR": ["Bhubaneswar", "Cuttack", "Rourkela"],
    "IN-CG": ["Raipur", "Bilaspur"],
    "IN-AR": ["Itanagar"],
}

# Approximate lat/lon centres per region (for map display later)
REGION_COORDS = {
    "IN-MH": (19.08, 72.88), "IN-KA": (12.97, 77.59), "IN-KL": (9.93, 76.27),
    "IN-TN": (13.08, 80.27), "IN-DL": (28.61, 77.21), "IN-GJ": (23.02, 72.57),
    "IN-RJ": (26.92, 75.79), "IN-UP": (26.85, 80.95), "IN-WB": (22.57, 88.36),
    "IN-AP": (17.69, 83.22), "IN-TS": (17.39, 78.49), "IN-BR": (25.61, 85.14),
    "IN-MP": (23.26, 77.41), "IN-HR": (28.46, 77.03), "IN-PB": (30.73, 76.78),
    "IN-GA": (15.50, 73.83), "IN-JH": (23.35, 85.33), "IN-OR": (20.30, 85.82),
    "IN-CG": (21.25, 81.63), "IN-AR": (27.10, 93.62),
}

HOSPITAL_NAMES = [
    "District General Hospital", "Civil Hospital", "Government Medical College",
    "Primary Health Centre", "Community Health Centre", "Sub-District Hospital",
    "Referral Hospital", "Specialty Hospital",
]

BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

CRITICAL_DRUGS = [
    "Paracetamol", "Amoxicillin", "ORS Sachets", "IV Fluids",
    "Antimalarials", "Insulin", "Doxycycline", "Azithromycin",
]


def _uid() -> str:
    return str(uuid.uuid4())[:8]


def _rand_phone() -> str:
    return f"+91-{random.randint(7000000000, 9999999999)}"


def _health_score(status: str) -> float:
    if status == "operational":
        return round(random.uniform(70, 100), 1)
    elif status == "degraded":
        return round(random.uniform(40, 69), 1)
    elif status == "critical":
        return round(random.uniform(10, 39), 1)
    return 0.0


def _pick_status(weights=(0.60, 0.25, 0.12, 0.03)):
    return random.choices(
        ["operational", "degraded", "critical", "offline"],
        weights=weights,
        k=1,
    )[0]


def _jitter(lat, lon):
    return round(lat + random.uniform(-0.3, 0.3), 4), round(lon + random.uniform(-0.3, 0.3), 4)


def _last_updated():
    dt = datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 720))
    return dt.isoformat()


# ---------------------------------------------------------------------------
# Generators per institution type
# ---------------------------------------------------------------------------

def _gen_hospitals():
    docs = []
    for region in REGIONS:
        cities = REGION_CITIES.get(region, ["City"])
        for city in cities:
            name_base = random.choice(HOSPITAL_NAMES)
            name = f"{city} {name_base}"
            status = _pick_status()
            beds_total = random.randint(50, 500)
            beds_avail = int(beds_total * random.uniform(0.05, 0.60)) if status != "offline" else 0
            icu_total = random.randint(5, 50)
            icu_avail = int(icu_total * random.uniform(0.0, 0.50)) if status != "offline" else 0
            lat, lon = _jitter(*REGION_COORDS.get(region, (20, 78)))
            docs.append({
                "institution_id": f"HOSP-{_uid()}",
                "name": name,
                "type": "hospital",
                "region_id": region,
                "lat": lat, "lon": lon,
                "address": f"{city}, {region}",
                "contact_phone": _rand_phone(),
                "status": status,
                "health_score": _health_score(status),
                "status_detail": {
                    "beds_total": beds_total,
                    "beds_available": beds_avail,
                    "icu_total": icu_total,
                    "icu_available": icu_avail,
                    "ventilators_total": random.randint(2, 30),
                    "ventilators_available": random.randint(0, 15),
                    "staff_on_duty": random.randint(10, 200),
                    "oxygen_cylinders": random.randint(5, 100),
                },
                "last_updated": _last_updated(),
            })
    return docs


def _gen_ambulances():
    docs = []
    for region in REGIONS[:15]:
        cities = REGION_CITIES.get(region, ["City"])[:1]
        for city in cities:
            status = _pick_status()
            fleet = random.randint(5, 30)
            lat, lon = _jitter(*REGION_COORDS.get(region, (20, 78)))
            docs.append({
                "institution_id": f"AMBU-{_uid()}",
                "name": f"{city} Ambulance Service",
                "type": "ambulance",
                "region_id": region,
                "lat": lat, "lon": lon,
                "contact_phone": _rand_phone(),
                "status": status,
                "health_score": _health_score(status),
                "status_detail": {
                    "fleet_size": fleet,
                    "active_vehicles": random.randint(1, fleet),
                    "avg_response_min": round(random.uniform(5, 25), 1),
                    "dispatched": random.randint(0, 5),
                },
                "last_updated": _last_updated(),
            })
    return docs


def _gen_fire_stations():
    docs = []
    for region in REGIONS[:12]:
        cities = REGION_CITIES.get(region, ["City"])[:1]
        for city in cities:
            status = _pick_status((0.70, 0.20, 0.08, 0.02))
            total = random.randint(3, 15)
            lat, lon = _jitter(*REGION_COORDS.get(region, (20, 78)))
            docs.append({
                "institution_id": f"FIRE-{_uid()}",
                "name": f"{city} Fire & Rescue",
                "type": "fire_station",
                "region_id": region,
                "lat": lat, "lon": lon,
                "contact_phone": _rand_phone(),
                "status": status,
                "health_score": _health_score(status),
                "status_detail": {
                    "active_units": random.randint(1, total),
                    "total_units": total,
                    "hazmat_available": random.random() > 0.4,
                    "shelter_capacity": random.randint(50, 500),
                },
                "last_updated": _last_updated(),
            })
    return docs


def _gen_labs():
    docs = []
    for region in REGIONS[:15]:
        cities = REGION_CITIES.get(region, ["City"])[:1]
        for city in cities:
            status = _pick_status()
            capacity = random.randint(50, 500)
            lat, lon = _jitter(*REGION_COORDS.get(region, (20, 78)))
            docs.append({
                "institution_id": f"LAB-{_uid()}",
                "name": f"{city} Public Health Lab",
                "type": "lab",
                "region_id": region,
                "lat": lat, "lon": lon,
                "contact_phone": _rand_phone(),
                "status": status,
                "health_score": _health_score(status),
                "status_detail": {
                    "daily_capacity": capacity,
                    "tests_today": random.randint(10, capacity),
                    "backlog": random.randint(0, int(capacity * 0.8)),
                    "turnaround_hours": round(random.uniform(2, 48), 1),
                    "test_types": random.sample(
                        ["RT-PCR", "Rapid Antigen", "ELISA", "Blood Culture", "CBC", "Serology"],
                        k=random.randint(2, 5),
                    ),
                },
                "last_updated": _last_updated(),
            })
    return docs


def _gen_pharmacies():
    docs = []
    for region in REGIONS[:12]:
        cities = REGION_CITIES.get(region, ["City"])[:1]
        for city in cities:
            status = _pick_status()
            stock_pct = round(random.uniform(15, 100), 1)
            lat, lon = _jitter(*REGION_COORDS.get(region, (20, 78)))
            drugs = {d: random.randint(0, 500) for d in random.sample(CRITICAL_DRUGS, k=5)}
            docs.append({
                "institution_id": f"PHAR-{_uid()}",
                "name": f"{city} Medical Supply Depot",
                "type": "pharmacy",
                "region_id": region,
                "lat": lat, "lon": lon,
                "contact_phone": _rand_phone(),
                "status": status,
                "health_score": _health_score(status),
                "status_detail": {
                    "critical_drugs_stock": drugs,
                    "stock_health_pct": stock_pct,
                    "last_restock_date": (datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
                },
                "last_updated": _last_updated(),
            })
    return docs


def _gen_district_admin():
    docs = []
    for region in REGIONS:
        lat, lon = _jitter(*REGION_COORDS.get(region, (20, 78)))
        status = _pick_status((0.75, 0.18, 0.05, 0.02))
        docs.append({
            "institution_id": f"DADM-{_uid()}",
            "name": f"{region} District Collectorate",
            "type": "district_admin",
            "region_id": region,
            "lat": lat, "lon": lon,
            "contact_phone": _rand_phone(),
            "status": status,
            "health_score": _health_score(status),
            "status_detail": {
                "active_directives": random.randint(0, 12),
                "evacuation_plan_ready": random.random() > 0.3,
                "budget_allocated_lakhs": round(random.uniform(10, 500), 2),
                "coordination_score": round(random.uniform(40, 98), 1),
            },
            "last_updated": _last_updated(),
        })
    return docs


def _gen_police():
    docs = []
    for region in REGIONS[:15]:
        cities = REGION_CITIES.get(region, ["City"])[:1]
        for city in cities:
            status = _pick_status((0.75, 0.18, 0.05, 0.02))
            lat, lon = _jitter(*REGION_COORDS.get(region, (20, 78)))
            docs.append({
                "institution_id": f"PLCE-{_uid()}",
                "name": f"{city} Police HQ",
                "type": "police",
                "region_id": region,
                "lat": lat, "lon": lon,
                "contact_phone": _rand_phone(),
                "status": status,
                "health_score": _health_score(status),
                "status_detail": {
                    "personnel_deployed": random.randint(20, 300),
                    "checkpoints_active": random.randint(0, 10),
                    "crowd_control_teams": random.randint(0, 5),
                    "patrol_vehicles": random.randint(2, 30),
                },
                "last_updated": _last_updated(),
            })
    return docs


def _gen_blood_banks():
    docs = []
    for region in REGIONS[:12]:
        cities = REGION_CITIES.get(region, ["City"])[:1]
        for city in cities:
            status = _pick_status()
            inv = {bt: random.randint(0, 60) for bt in BLOOD_TYPES}
            lat, lon = _jitter(*REGION_COORDS.get(region, (20, 78)))
            docs.append({
                "institution_id": f"BLDB-{_uid()}",
                "name": f"{city} Blood Bank",
                "type": "blood_bank",
                "region_id": region,
                "lat": lat, "lon": lon,
                "contact_phone": _rand_phone(),
                "status": status,
                "health_score": _health_score(status),
                "status_detail": {
                    "inventory": inv,
                    "units_expiring_soon": random.randint(0, 20),
                    "demand_today": random.randint(0, 30),
                },
                "last_updated": _last_updated(),
            })
    return docs


def _gen_wash():
    docs = []
    for region in REGIONS[:15]:
        lat, lon = _jitter(*REGION_COORDS.get(region, (20, 78)))
        status = _pick_status((0.55, 0.30, 0.12, 0.03))
        docs.append({
            "institution_id": f"WASH-{_uid()}",
            "name": f"{region} WASH Division",
            "type": "wash",
            "region_id": region,
            "lat": lat, "lon": lon,
            "contact_phone": _rand_phone(),
            "status": status,
            "health_score": _health_score(status),
            "status_detail": {
                "water_quality_index": round(random.uniform(30, 98), 1),
                "sanitation_coverage_pct": round(random.uniform(40, 95), 1),
                "sewage_surveillance_active": random.random() > 0.3,
                "contamination_alerts": random.randint(0, 5),
            },
            "last_updated": _last_updated(),
        })
    return docs


def _gen_ngos():
    ngo_names = [
        "Red Cross Chapter", "Médecins Sans Frontières Unit",
        "CARE India Branch", "Oxfam Relief Centre",
        "Doctors Without Borders Unit", "Save the Children Office",
    ]
    docs = []
    for region in REGIONS[:10]:
        name = random.choice(ngo_names)
        lat, lon = _jitter(*REGION_COORDS.get(region, (20, 78)))
        status = _pick_status((0.65, 0.25, 0.08, 0.02))
        docs.append({
            "institution_id": f"NGO-{_uid()}",
            "name": f"{name} — {region}",
            "type": "ngo",
            "region_id": region,
            "lat": lat, "lon": lon,
            "contact_phone": _rand_phone(),
            "status": status,
            "health_score": _health_score(status),
            "status_detail": {
                "volunteers_active": random.randint(5, 200),
                "relief_camps": random.randint(0, 5),
                "supply_kits_available": random.randint(10, 1000),
                "beneficiaries_served": random.randint(50, 5000),
            },
            "last_updated": _last_updated(),
        })
    return docs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def seed():
    db = get_db()
    col = db["institutions"]

    # Clear existing
    deleted = col.delete_many({})
    print(f"🗑️  Cleared {deleted.deleted_count} existing institution records")

    all_docs = []
    generators = [
        ("Hospitals", _gen_hospitals),
        ("Ambulances", _gen_ambulances),
        ("Fire Stations", _gen_fire_stations),
        ("Labs", _gen_labs),
        ("Pharmacies", _gen_pharmacies),
        ("District Admin", _gen_district_admin),
        ("Police", _gen_police),
        ("Blood Banks", _gen_blood_banks),
        ("WASH", _gen_wash),
        ("NGOs", _gen_ngos),
    ]

    for label, gen_fn in generators:
        docs = gen_fn()
        all_docs.extend(docs)
        print(f"  ✓ {label}: {len(docs)} institutions")

    if all_docs:
        col.insert_many(all_docs)

    # Create indexes
    col.create_index("institution_id", unique=True)
    col.create_index("type")
    col.create_index("region_id")
    col.create_index("status")

    print(f"\n✅ Seeded {len(all_docs)} institutions across 10 categories")


if __name__ == "__main__":
    seed()

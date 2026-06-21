"""
seeds/seed_locations_v2.py
Run with: flask shell < seeds/seed_locations_v2.py
Or: python seeds/seed_locations_v2.py (if FLASK_APP is set)

Expands LocationIndex to cover Accra and Kumasi.
Safe to re-run — skips existing slugs.
"""

from app import create_app
from app.extensions import db
from app.models.location import LocationIndex

app = create_app()

LOCATIONS = [
    # ── ACCRA ──────────────────────────────────────────────────
    {"area_name": "Accra (All Areas)",      "city": "Accra",  "slug": "accra",                    "lat": 5.6037,   "lng": -0.1870},
    {"area_name": "Achimota",               "city": "Accra",  "slug": "achimota",                  "lat": 5.6350,   "lng": -0.2319},
    {"area_name": "Adabraka",               "city": "Accra",  "slug": "adabraka",                  "lat": 5.5656,   "lng": -0.2100},
    {"area_name": "Airport Residential",    "city": "Accra",  "slug": "airport-residential",       "lat": 5.6052,   "lng": -0.1718},
    {"area_name": "Atomic",                 "city": "Accra",  "slug": "atomic",                    "lat": 5.6750,   "lng": -0.2350},
    {"area_name": "Cantonments",            "city": "Accra",  "slug": "cantonments",               "lat": 5.5800,   "lng": -0.1750},
    {"area_name": "Dansoman",               "city": "Accra",  "slug": "dansoman",                  "lat": 5.5489,   "lng": -0.2536},
    {"area_name": "Dodowa",                 "city": "Accra",  "slug": "dodowa",                    "lat": 5.8897,   "lng": -0.1276},
    {"area_name": "East Legon",             "city": "Accra",  "slug": "east-legon",                "lat": 5.6366,   "lng": -0.1551},
    {"area_name": "Haatso",                 "city": "Accra",  "slug": "haatso",                    "lat": 5.6558,   "lng": -0.2150},
    {"area_name": "Kasoa",                  "city": "Accra",  "slug": "kasoa",                     "lat": 5.5333,   "lng": -0.4167},
    {"area_name": "La",                     "city": "Accra",  "slug": "la",                        "lat": 5.5680,   "lng": -0.1480},
    {"area_name": "Labone",                 "city": "Accra",  "slug": "labone",                    "lat": 5.5733,   "lng": -0.1667},
    {"area_name": "Madina",                 "city": "Accra",  "slug": "madina",                    "lat": 5.6800,   "lng": -0.1667},
    {"area_name": "North Legon",            "city": "Accra",  "slug": "north-legon",               "lat": 5.6700,   "lng": -0.1600},
    {"area_name": "Nungua",                 "city": "Accra",  "slug": "nungua",                    "lat": 5.5667,   "lng": -0.0833},
    {"area_name": "Osu",                    "city": "Accra",  "slug": "osu",                       "lat": 5.5558,   "lng": -0.1769},
    {"area_name": "Oyibi",                  "city": "Accra",  "slug": "oyibi",                     "lat": 5.7500,   "lng": -0.1167},
    {"area_name": "Spintex",                "city": "Accra",  "slug": "spintex",                   "lat": 5.6167,   "lng": -0.1000},
    {"area_name": "Tema",                   "city": "Accra",  "slug": "tema",                      "lat": 5.6698,   "lng": -0.0166},
    {"area_name": "Teshie",                 "city": "Accra",  "slug": "teshie",                    "lat": 5.5667,   "lng": -0.1167},
    {"area_name": "Tesano",                 "city": "Accra",  "slug": "tesano",                    "lat": 5.6000,   "lng": -0.2167},
    {"area_name": "Dzorwulu",               "city": "Accra",  "slug": "dzorwulu",                  "lat": 5.6050,   "lng": -0.2050},
    {"area_name": "Abelemkpe",              "city": "Accra",  "slug": "abelemkpe",                 "lat": 5.5983,   "lng": -0.2133},
    {"area_name": "Legon",                  "city": "Accra",  "slug": "legon",                     "lat": 5.6502,   "lng": -0.1869},
    {"area_name": "Tema Community 1",       "city": "Accra",  "slug": "tema-community-1",          "lat": 5.6698,   "lng": -0.0200},
    {"area_name": "Tema Community 25",      "city": "Accra",  "slug": "tema-community-25",         "lat": 5.7000,   "lng":  0.0200},
    # ── KUMASI ─────────────────────────────────────────────────
    {"area_name": "Kumasi (All Areas)",     "city": "Kumasi", "slug": "kumasi",                    "lat": 6.6885,   "lng": -1.6244},
    {"area_name": "Adum",                   "city": "Kumasi", "slug": "adum",                      "lat": 6.6900,   "lng": -1.6233},
    {"area_name": "Asokwa",                 "city": "Kumasi", "slug": "asokwa",                    "lat": 6.6700,   "lng": -1.6100},
    {"area_name": "Bantama",                "city": "Kumasi", "slug": "bantama",                   "lat": 6.7050,   "lng": -1.6300},
    {"area_name": "Danyame",                "city": "Kumasi", "slug": "danyame",                   "lat": 6.6750,   "lng": -1.6400},
    {"area_name": "Dichemso",               "city": "Kumasi", "slug": "dichemso",                  "lat": 6.6850,   "lng": -1.6350},
    {"area_name": "Ejisu",                  "city": "Kumasi", "slug": "ejisu",                     "lat": 6.7200,   "lng": -1.4700},
    {"area_name": "Kentinkrono",            "city": "Kumasi", "slug": "kentinkrono",               "lat": 6.6600,   "lng": -1.6550},
    {"area_name": "Krofrom",                "city": "Kumasi", "slug": "krofrom",                   "lat": 6.6950,   "lng": -1.6150},
    {"area_name": "Kwadaso",                "city": "Kumasi", "slug": "kwadaso",                   "lat": 6.7100,   "lng": -1.6600},
    {"area_name": "Manhyia",                "city": "Kumasi", "slug": "manhyia",                   "lat": 6.7050,   "lng": -1.6167},
    {"area_name": "Nhyiaeso",               "city": "Kumasi", "slug": "nhyiaeso",                  "lat": 6.6800,   "lng": -1.5900},
    {"area_name": "Oforikrom",              "city": "Kumasi", "slug": "oforikrom",                 "lat": 6.6600,   "lng": -1.5800},
    {"area_name": "Old Tafo",               "city": "Kumasi", "slug": "old-tafo",                  "lat": 6.7167,   "lng": -1.6000},
    {"area_name": "Patase",                 "city": "Kumasi", "slug": "patase",                    "lat": 6.7300,   "lng": -1.6400},
    {"area_name": "Suame",                  "city": "Kumasi", "slug": "suame",                     "lat": 6.7200,   "lng": -1.6300},
    {"area_name": "Tafo",                   "city": "Kumasi", "slug": "tafo",                      "lat": 6.7200,   "lng": -1.5950},
]

with app.app_context():
    inserted = 0
    skipped = 0
    for loc in LOCATIONS:
        exists = LocationIndex.query.filter_by(slug=loc["slug"]).first()
        if exists:
            skipped += 1
            continue
        row = LocationIndex(
            area_name=loc["area_name"],
            city=loc["city"],
            slug=loc["slug"],
            centroid_lat=loc["lat"],
            centroid_lng=loc["lng"],
            is_active=True,
        )
        db.session.add(row)
        inserted += 1
    db.session.commit()
    print(f"Done. Inserted: {inserted}, Skipped (already exist): {skipped}")

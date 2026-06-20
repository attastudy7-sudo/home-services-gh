import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.extensions import db
from app.models.location import LocationIndex

ACCRA_AREAS = [
    ("Accra (All Areas)",  "Accra", "accra",                    5.5600, -0.2000),
    ("East Legon",         "Accra", "accra-east-legon",         5.6321, -0.1617),
    ("Osu",                "Accra", "accra-osu",                5.5558, -0.1774),
    ("Labone",             "Accra", "accra-labone",             5.5650, -0.1700),
    ("Cantonments",        "Accra", "accra-cantonments",        5.5700, -0.1800),
    ("Airport Residential","Accra", "accra-airport-residential",5.6050, -0.1733),
    ("Adabraka",           "Accra", "accra-adabraka",           5.5600, -0.2100),
    ("Dansoman",           "Accra", "accra-dansoman",           5.5370, -0.2560),
    ("Achimota",           "Accra", "accra-achimota",           5.6200, -0.2300),
    ("Spintex",            "Accra", "accra-spintex",            5.6400, -0.1300),
    ("Tema",               "Accra", "accra-tema",               5.6698, -0.0166),
    ("Madina",             "Accra", "accra-madina",             5.6750, -0.1700),
    ("Haatso",             "Accra", "accra-haatso",             5.6600, -0.2000),
    ("Atomic",             "Accra", "accra-atomic",             5.6500, -0.2200),
    ("North Legon",        "Accra", "accra-north-legon",        5.6500, -0.1700),
    ("Nungua",             "Accra", "accra-nungua",             5.5800, -0.1000),
    ("La",                 "Accra", "accra-la",                 5.5600, -0.1600),
    ("Teshie",             "Accra", "accra-teshie",             5.5900, -0.0900),
    ("Kasoa",              "Accra", "accra-kasoa",              5.5300, -0.4200),
    ("Oyibi",              "Accra", "accra-oyibi",              5.7600, -0.1000),
    ("Dodowa",             "Accra", "accra-dodowa",             5.8900, -0.1300),
]


def run():
    app = create_app()
    with app.app_context():
        for area_name, city, slug, lat, lng in ACCRA_AREAS:
            exists = LocationIndex.query.filter_by(slug=slug).first()
            if not exists:
                db.session.add(LocationIndex(
                    area_name=area_name, city=city, slug=slug,
                    centroid_lat=lat, centroid_lng=lng
                ))
        db.session.commit()
        print(f"Seeded {len(ACCRA_AREAS)} location areas.")


if __name__ == '__main__':
    run()

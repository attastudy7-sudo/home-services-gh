import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.extensions import db
from app.models.service import ServiceCategory, ServiceSubcategory

CATEGORIES = [
    ("Plumbing",                "plumbing",           1, [
        ("Burst pipe repair",    "burst-pipe-repair"),
        ("Toilet installation",  "toilet-installation"),
        ("Water tank install",   "water-tank-install"),
        ("Geyser repair",        "geyser-repair"),
        ("Leak detection",       "leak-detection"),
    ]),
    ("AC & Appliances",         "ac-appliances",      2, [
        ("AC installation",      "ac-installation"),
        ("AC servicing",         "ac-servicing"),
        ("Fridge repair",        "fridge-repair"),
        ("Washing machine repair","washing-machine-repair"),
    ]),
    ("Electrical",              "electrical",         3, [
        ("Wiring & rewiring",    "wiring-rewiring"),
        ("Socket installation",  "socket-installation"),
        ("Generator servicing",  "generator-servicing"),
        ("Security lighting",    "security-lighting"),
    ]),
    ("Cleaning & Laundry",       "cleaning-pest",      4, [
        ("House cleaning",       "house-cleaning"),
        ("Post-construction clean","post-construction-clean"),
        ("Pest fumigation",      "pest-fumigation"),
        ("Termite treatment",    "termite-treatment"),
    ]),
    ("Painting",                "painting",           5, [
        ("Interior painting",    "interior-painting"),
        ("Exterior painting",    "exterior-painting"),
        ("Waterproofing",        "waterproofing"),
    ]),
    ("Carpentry & Furniture",   "carpentry-furniture",6, [
        ("Door installation",    "door-installation"),
        ("Furniture assembly",   "furniture-assembly"),
        ("Cabinet making",       "cabinet-making"),
    ]),
    ("Moving & Storage",        "moving-storage",     7, [
        ("Local house move",     "local-house-move"),
        ("Office relocation",    "office-relocation"),
        ("Item delivery",        "item-delivery"),
    ]),
    ("Renovation & Construction","renovation-construction",8,[
        ("Bathroom renovation",  "bathroom-renovation"),
        ("Kitchen renovation",   "kitchen-renovation"),
        ("Tiling & flooring",    "tiling-flooring"),
        ("Civil contractor",     "civil-contractor"),
    ]),
]


def run():
    app = create_app()
    with app.app_context():
        for name, slug, order, subs in CATEGORIES:
            cat = ServiceCategory.query.filter_by(slug=slug).first()
            if not cat:
                cat = ServiceCategory(name=name, slug=slug, sort_order=order)
                db.session.add(cat)
                db.session.flush()
            for sub_name, sub_slug in subs:
                if not ServiceSubcategory.query.filter_by(slug=sub_slug).first():
                    db.session.add(ServiceSubcategory(
                        category_id=cat.id, name=sub_name, slug=sub_slug
                    ))
        db.session.commit()
        print("Seeded 8 categories and all subcategories.")


if __name__ == '__main__':
    run()

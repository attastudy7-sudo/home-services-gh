"""
seeds/seed_pros.py
Run: flask shell < seeds/seed_pros.py
Or:  python seeds/seed_pros.py (if FLASK_APP is set)

Seeds approved pro profiles across all categories (3+ per category).
Safe to re-run — skips existing slugs.
"""

import re
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.pro import ProProfile, ProCategory, ProSubcategory, ProServiceArea as ProServiceAreaModel
from app.models.service import ServiceCategory, ServiceSubcategory
from app.models.location import LocationIndex

app = create_app()

PROS = [
    # ── PLUMBING ──
    {"name": "Kofi Mensah",       "email": "kofi.mensah@example.com",   "phone": "0201000001", "cat_slug": "plumbing",      "sub_slug": "Burst pipe repair",      "city": "Accra",  "rate": 80,  "bio": "Licensed plumber with 12 years of experience handling residential and commercial jobs."},
    {"name": "John Tetteh",       "email": "john.tetteh@example.com",   "phone": "0201000002", "cat_slug": "plumbing",      "sub_slug": "Toilet installation",    "city": "Accra",  "rate": 75,  "bio": "Specialist in toilet installations, leak fixes, and water heater repairs."},
    {"name": "Samuel Asare",      "email": "samuel.asare@example.com",  "phone": "0201000003", "cat_slug": "plumbing",      "sub_slug": "Water tank install",     "city": "Kumasi", "rate": 70,  "bio": "Reliable plumber serving the Kumasi metropolis for over 8 years."},

    # ── AC & APPLIANCES ──
    {"name": "Daniel Osei",       "email": "daniel.osei@example.com",   "phone": "0201000004", "cat_slug": "ac-appliances",  "sub_slug": "AC installation",        "city": "Accra",  "rate": 120, "bio": "Certified HVAC technician with experience in split AC, inverter, and central systems."},
    {"name": "Michael Sarpong",   "email": "michael.sarpong@example.com","phone": "0201000005", "cat_slug": "ac-appliances",  "sub_slug": "Fridge repair",          "city": "Accra",  "rate": 90,  "bio": "Expert in refrigerator and freezer repairs for all major brands."},
    {"name": "Eric Amankwah",     "email": "eric.amankwah@example.com", "phone": "0201000006", "cat_slug": "ac-appliances",  "sub_slug": "Washing machine repair",  "city": "Kumasi", "rate": 85,  "bio": "Washing machine, dryer, and dishwasher repair specialist in Kumasi."},

    # ── ELECTRICAL ──
    {"name": "Joseph Ampofo",    "email": "joseph.ampofo@example.com",  "phone": "0201000007", "cat_slug": "electrical",      "sub_slug": "Wiring & rewiring",      "city": "Accra",  "rate": 90,  "bio": "Master electrician with 15 years of experience in residential wiring and rewiring."},
    {"name": "William Agyapong", "email": "william.agyapong@example.com","phone": "0201000008", "cat_slug": "electrical",      "sub_slug": "Socket installation",    "city": "Accra",  "rate": 70,  "bio": "Specializes in socket installations, lighting, and home automation."},
    {"name": "George Dadzie",    "email": "george.dadzie@example.com",  "phone": "0201000009", "cat_slug": "electrical",      "sub_slug": "Generator servicing",    "city": "Kumasi", "rate": 100, "bio": "Generator, inverter, and electrical panel specialist based in Kumasi."},

    # ── CATERING ──
    {"name": "Abena Oforiwaa",   "email": "abena.oforiwaa@example.com","phone": "0201000010", "cat_slug": "catering",        "sub_slug": "Event catering",         "city": "Accra",  "rate": 150, "bio": "Award-winning caterer for weddings, corporate events, and private parties."},
    {"name": "Grace Adjei",      "email": "grace.adjei@example.com",   "phone": "0201000011", "cat_slug": "catering",        "sub_slug": "Traditional Ghanaian dishes","city": "Accra","rate": 120, "bio": "Authentic Ghanaian cuisine — jollof, fufu, waakye, and more."},
    {"name": "Comfort Nyarko",   "email": "comfort.nyarko@example.com","phone": "0201000012", "cat_slug": "catering",        "sub_slug": "Cake baking & decorating","city": "Kumasi","rate": 130, "bio": "Custom cakes, pastries, and confectionery for all occasions in Kumasi."},

    # ── CLEANING & LAUNDRY ──
    {"name": "Ama Serwaa",       "email": "ama.serwaa@example.com",    "phone": "0201000013", "cat_slug": "cleaning-pest",   "sub_slug": "House cleaning",         "city": "Accra",  "rate": 60,  "bio": "Thorough and reliable home cleaning services in Accra."},
    {"name": "Beatrice Anane",   "email": "beatrice.anane@example.com","phone": "0201000014", "cat_slug": "cleaning-pest",   "sub_slug": "Post-construction clean","city": "Accra",  "rate": 80,  "bio": "Post-construction and deep cleaning specialist for homes and offices."},
    {"name": "Joyce Asante",     "email": "joyce.asante@example.com",  "phone": "0201000015", "cat_slug": "cleaning-pest",   "sub_slug": "Pest fumigation",        "city": "Kumasi", "rate": 100, "bio": "Certified pest control specialist serving Kumasi and surrounding areas."},

    # ── PAINTING ──
    {"name": "Samuel Ofori",     "email": "samuel.ofori@example.com",  "phone": "0201000016", "cat_slug": "painting",         "sub_slug": "Interior painting",      "city": "Accra",  "rate": 70,  "bio": "Interior and exterior painting with premium finishes."},
    {"name": "Patrick Dwumoh",   "email": "patrick.dwumoh@example.com","phone": "0201000017", "cat_slug": "painting",         "sub_slug": "Exterior painting",      "city": "Accra",  "rate": 75,  "bio": "Expert in exterior painting, waterproofing, and wall texture."},
    {"name": "Isaac Mensah",     "email": "isaac.mensah@example.com",  "phone": "0201000018", "cat_slug": "painting",         "sub_slug": "Waterproofing",          "city": "Kumasi", "rate": 80,  "bio": "Waterproofing and painting professional with 7 years of experience."},

    # ── CARPENTRY & FURNITURE ──
    {"name": "Kwame Antwi",      "email": "kwame.antwi@example.com",   "phone": "0201000019", "cat_slug": "carpentry-furniture","sub_slug": "Door installation",     "city": "Accra",  "rate": 90,  "bio": "Custom doors, windows, and wooden installations. 10 years experience."},
    {"name": "Yaw Boateng",      "email": "yaw.boateng@example.com",   "phone": "0201000020", "cat_slug": "carpentry-furniture","sub_slug": "Furniture assembly",     "city": "Accra",  "rate": 65,  "bio": "Furniture assembly, repairs, and custom pieces."},
    {"name": "Peter Addai",      "email": "peter.addai@example.com",   "phone": "0201000021", "cat_slug": "carpentry-furniture","sub_slug": "Cabinet making",         "city": "Kumasi", "rate": 95,  "bio": "Master cabinet maker in Kumasi, specializing in kitchen and wardrobe cabinets."},

    # ── MOVING & STORAGE ──
    {"name": "Emmanuel Asare",   "email": "emmanuel.asare@example.com","phone": "0201000022", "cat_slug": "moving-storage",   "sub_slug": "Local house move",       "city": "Accra",  "rate": 200, "bio": "Reliable moving team for local house moves across Accra. Full service."},
    {"name": "Richard Koomson",  "email": "richard.koomson@example.com","phone": "0201000023","cat_slug": "moving-storage",   "sub_slug": "Office relocation",      "city": "Accra",  "rate": 250, "bio": "Office relocation specialist — secure, fast, and insured."},
    {"name": "Stephen Amoah",    "email": "stephen.amoah@example.com", "phone": "0201000024", "cat_slug": "moving-storage",   "sub_slug": "Item delivery",          "city": "Kumasi", "rate": 80,  "bio": "Item delivery and transport services within Kumasi."},

    # ── RENOVATION & CONSTRUCTION ──
    {"name": "Thomas Asiamah",   "email": "thomas.asiamah@example.com","phone": "0201000025", "cat_slug": "renovation-construction","sub_slug": "Bathroom renovation", "city": "Accra",  "rate": 300, "bio": "Full bathroom and kitchen renovation services in Accra."},
    {"name": "James Kwao",       "email": "james.kwao@example.com",    "phone": "0201000026", "cat_slug": "renovation-construction","sub_slug": "Tiling & flooring",    "city": "Accra",  "rate": 180, "bio": "Professional tiling and flooring for residential and commercial spaces."},
    {"name": "Joseph Tetteh",    "email": "joseph.tetteh2@example.com","phone": "0201000027", "cat_slug": "renovation-construction","sub_slug": "Kitchen renovation",   "city": "Kumasi", "rate": 280, "bio": "Kitchen remodeling and renovation expert serving Kumasi."},
]

with app.app_context():
    inserted = 0
    skipped = 0

    for p in PROS:
        slug = re.sub(r'[^a-z0-9]+', '-', p["name"].lower()).strip('-')

        existing_pro = ProProfile.query.filter_by(slug=slug).first()
        if existing_pro:
            skipped += 1
            continue

        existing_user = User.query.filter_by(email=p["email"]).first()
        if existing_user:
            skipped += 1
            continue

        cat = ServiceCategory.query.filter_by(slug=p["cat_slug"]).first()
        if not cat:
            print(f"  WARN: category '{p['cat_slug']}' not found, skipping {p['name']}")
            skipped += 1
            continue

        sub = ServiceSubcategory.query.filter_by(name=p["sub_slug"], category_id=cat.id).first()
        if not sub:
            sub = ServiceSubcategory.query.filter(
                ServiceSubcategory.name.ilike(p["sub_slug"]),
                ServiceSubcategory.category_id == cat.id
            ).first()

        user = User(
            email=p["email"],
            phone=p["phone"],
            full_name=p["name"],
            is_verified=True,
            is_active=True,
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.flush()

        pro = ProProfile(
            user_id=user.id,
            business_name=p["name"],
            slug=slug,
            bio=p["bio"],
            years_experience=8,
            base_hourly_rate=p["rate"],
            verification_status="approved",
            is_available=True,
            avg_rating=round(3.5 + (hash(p["name"]) % 15) / 10, 1),
            total_reviews=hash(p["name"]) % 30 + 3,
            total_jobs=hash(p["name"]) % 50 + 10,
        )
        db.session.add(pro)
        db.session.flush()

        db.session.add(ProCategory(pro_id=pro.id, category_id=cat.id))

        if sub:
            db.session.add(ProSubcategory(pro_id=pro.id, subcategory_id=sub.id))

        area_ids = []
        if p["city"] == "Accra":
            area_ids = [r.id for r in LocationIndex.query.filter_by(city="Accra").limit(4).all()]
        elif p["city"] == "Kumasi":
            area_ids = [r.id for r in LocationIndex.query.filter_by(city="Kumasi").limit(4).all()]

        for aid in area_ids:
            db.session.add(ProServiceAreaModel(pro_id=pro.id, location_index_id=aid, radius_km=10))

        inserted += 1

    db.session.commit()
    print(f"Done. Inserted: {inserted}, Skipped (already exist): {skipped}")

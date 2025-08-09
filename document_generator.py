# Generate 20 diverse mock assessment templates (10 VirginAir Australia, 10 AirTransat)
# Save as JSONL files and a combined JSONL for convenience.

import json
from pathlib import Path
from datetime import datetime, timedelta
import random
import uuid

random.seed(42)

base_dir = Path("data")
base_dir.mkdir(parents=True, exist_ok=True)

# -------------------------
# Helper generators
# -------------------------
def rand_date(start_year=2023, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    d = start + timedelta(days=random.randint(0, delta.days))
    return d.strftime("%Y-%m-%d")

def rand_bool(p_true=0.5):
    return random.random() < p_true

def nm_to_km(nm):
    return round(nm * 1.852, 1)

def rand_uuid():
    return str(uuid.uuid4())

# Airports
au_airports = ["SYD","MEL","BNE","PER","ADL","CBR","OOL","CNS","DRW","HBA","LST","AVV","MCY","NRT","AKL"]
ca_airports = ["YUL","YYZ","YVR","YOW","YQB","YEG","YYC","YHZ","YWG","YXE","YDF","YTZ","YQB","YQM"]
aircraft_va = ["B737-800","B737-MAX","A320","A321neo"]
aircraft_at = ["A321LR","A330-200","B737-800","A321neo"]
approaches = ["ILS Cat I","ILS Cat II","ILS Cat IIIA","RNP LNAV","RNP LNAV/VNAV","RNAV GPS/GNSS","VOR","VISUAL APCH"]
takeoff_opts = ["Day","Night"]

# Pilot names
va_pilots = ["Alex Nguyen","Priya Singh","James Carter","Mika Tan","Chris Johnson","Sophie Lee","Daniel O'Connor","Hannah Wright","Liam Patel","Emily Chen"]
at_pilots = ["Marc Tremblay","Sarah Ouellet","David Martin","Amélie Roy","Jason Wong","Olivia Nguyen","Ethan Brown","Chantal Dubois","Noah Wilson","Émile Gagnon"]

# Distances (nm) by rough route mapping (randomized if unknown)
def route_nm(dep, arr):
    rough = {
        ("SYD","MEL"): 381, ("SYD","BNE"): 385, ("SYD","PER"): 1784, ("SYD","LST"): 479,
        ("YUL","YYZ"): 286, ("YUL","YVR"): 2045, ("YYZ","YVR"): 2081, ("YUL","YQB"): 145,
        ("YYZ","YHZ"): 713, ("YVR","YYC"): 365
    }
    if (dep, arr) in rough: return rough[(dep, arr)]
    if (arr, dep) in rough: return rough[(arr, dep)]
    return random.randint(120, 2200)

# -------------------------
# VirginAir Australia template style (col2 / "Fields" list with dropdown/checkbox/etc.)
# -------------------------
def make_virginair_record(i):
    dep = random.choice(au_airports)
    arr = random.choice([a for a in au_airports if a != dep])
    nm = route_nm(dep, arr)
    km = nm_to_km(nm)

    pf = rand_bool(0.6)
    pm = not pf if rand_bool(0.9) else rand_bool(0.5)  # usually exclusive, but may be messy

    # Some records will have AUTO LAND unchecked or missing
    include_autoland = rand_bool(0.8)
    autoland_val = "true" if rand_bool(0.3) else None

    fields = [
        {
            "Identifier": "00000000-0000-0000-0000-000000000000",
            "Index": 0, "ColIndex": 0, "Type": "dropdown", "Label": "Aircraft",
            "Value": random.choice(aircraft_va),
            "Values": None, "ValueSource": None, "Comment": None,
            "Configuration": {"Name": "LT_AIRCRAFT", "Items": "\n".join(aircraft_va), "Mandatory": True},
            "UserOnBehalfId": 0
        },
        {"Identifier":"00000000-0000-0000-0000-000000000000","Index":1,"ColIndex":0,"Type":"dropdown","Label":"From","Value":dep,
         "Values":None,"ValueSource":None,"Comment":None,"Configuration":{"Name":"LT_FROM","Items":"\n".join(au_airports),"Mandatory":True},"UserOnBehalfId":0},
        {"Identifier":"00000000-0000-0000-0000-000000000000","Index":2,"ColIndex":0,"Type":"dropdown","Label":"To","Value":arr,
         "Values":None,"ValueSource":None,"Comment":None,"Configuration":{"Name":"LT_TO","Items":"\n".join(au_airports),"Mandatory":True},"UserOnBehalfId":0},
        {"Identifier":"00000000-0000-0000-0000-000000000000","Index":3,"ColIndex":0,"Type":"checkbox","Label":"Pilot Flying (PF)","Value": "true" if pf else None,
         "Values":None,"ValueSource":None,"Comment":None,"Configuration":{"Name":"LT_PF","Mandatory":False},"UserOnBehalfId":0},
        {"Identifier":"00000000-0000-0000-0000-000000000000","Index":4,"ColIndex":0,"Type":"checkbox","Label":"Pilot Monitoring (PM)","Value": "true" if pm else None,
         "Values":None,"ValueSource":None,"Comment":None,"Configuration":{"Name":"LT_PM","Mandatory":False},"UserOnBehalfId":0},
    ]

    if include_autoland:
        fields.append({"Identifier":"00000000-0000-0000-0000-000000000000","Index":5,"ColIndex":0,"Type":"checkbox","Label":"AUTO LAND","Value": autoland_val,
                       "Values":None,"ValueSource":None,"Comment":None,"Configuration":{"Name":"LT_AUTO_LDG"},"UserOnBehalfId":0})

    # Optional PF-only section
    fields += [
        {"Identifier":"00000000-0000-0000-0000-000000000000","Index":0,"ColIndex":1,"Type":"label","Label":"PF-only section","Value":None,
         "Values":None,"ValueSource":None,"Comment":None,"Configuration":{},"UserOnBehalfId":0},
        {"Identifier":"00000000-0000-0000-0000-000000000000","Index":1,"ColIndex":1,"Type":"checkbox","Label":"LVO TKOFF","Value": "true" if rand_bool(0.2) else None,
         "Values":None,"ValueSource":None,"Comment":None,"Configuration":{"Name":"LT_LVO_TKOFF"},"UserOnBehalfId":0},
        {"Identifier":"00000000-0000-0000-0000-000000000000","Index":2,"ColIndex":1,"Type":"dropdown","Label":"Take-off","Value": random.choice(takeoff_opts),
         "Values":None,"ValueSource":None,"Comment":None,"Configuration":{"Name":"LT_TKOFF","Items":"\n".join(takeoff_opts),"Mandatory":False},"UserOnBehalfId":0},
        {"Identifier":"00000000-0000-0000-0000-000000000000","Index":3,"ColIndex":1,"Type":"dropdown","Label":"Approach","Value": random.choice(approaches),
         "Values":None,"ValueSource":None,"Comment":None,"Configuration":{"Name":"LT_APCH","Items":"\n".join(approaches)},"UserOnBehalfId":0},
        {"Identifier":"00000000-0000-0000-0000-000000000000","Index":4,"ColIndex":1,"Type":"dropdown","Label":"Landing","Value": random.choice(takeoff_opts),
         "Values":None,"ValueSource":None,"Comment":None,"Configuration":{"Name":"LT_LDG","Items":"\n".join(takeoff_opts)},"UserOnBehalfId":0},
    ]

    # Optional candidate and distance (not always present)
    if rand_bool(0.8):
        fields.append({"Identifier":rand_uuid(),"Index":5,"ColIndex":1,"Type":"text","Label":"Candidate","Value": random.choice(va_pilots),
                       "Values":None,"ValueSource":None,"Comment":None,"Configuration":{"Name":"LT_CANDIDATE"},"UserOnBehalfId":0})
    if rand_bool(0.7):
        fields.append({"Identifier":rand_uuid(),"Index":6,"ColIndex":1,"Type":"number","Label":"Distance (NM)","Value": str(nm),
                       "Values":None,"ValueSource":None,"Comment":None,"Configuration":{"Name":"LT_DIST_NM"},"UserOnBehalfId":0})
    if rand_bool(0.4):
        fields.append({"Identifier":rand_uuid(),"Index":7,"ColIndex":1,"Type":"number","Label":"Distance (KM)","Value": str(km),
                       "Values":None,"ValueSource":None,"Comment":None,"Configuration":{"Name":"LT_DIST_KM"},"UserOnBehalfId":0})

    record = {
        "Airline": "VirginAir Australia",
        "TrainingType": "Flight Training",
        "TemplateVersion": f"VA-FT-{i+1:02d}",
        "Date": rand_date(),
        "Type": "col2",
        "Fields": fields,
        "HasAssessmentFields": False
    }
    return record

# -------------------------
# AirTransat template style (col1 / mixed fields, nested structures)
# -------------------------
def make_airtransat_record(i):
    dep = random.choice(ca_airports)
    arr = random.choice([a for a in ca_airports if a != dep])
    nm = route_nm(dep, arr)
    km = nm_to_km(nm)

    pf = rand_bool(0.5)
    autoland = rand_bool(0.25)

    # Different naming conventions / nesting to simulate diversity
    fields = []

    # Sometimes encapsulate identity inside a nested object field
    if rand_bool(0.7):
        fields.append({
            "Identifier": "00000000-0000-0000-0000-000000000000",
            "Index": 0, "ColIndex": 0, "Type": "object", "Label": "Crew",
            "Value": {
                "primary": random.choice(at_pilots),
                "role": "PF" if pf else "PM"
            },
            "Configuration": {"Name": "AT_CREW"}
        })
    else:
        fields.append({
            "Identifier": rand_uuid(), "Index": 0, "ColIndex": 0, "Type": "text",
            "Label": "Assessed Pilot", "Value": random.choice(at_pilots),
            "Configuration": {"Name": "AT_PILOT"}
        })
        fields.append({
            "Identifier": rand_uuid(), "Index": 1, "ColIndex": 0, "Type": "dropdown",
            "Label": "Role", "Value": "PF" if pf else "PM",
            "Configuration": {"Name": "AT_ROLE", "Items": "PF\nPM"}
        })

    # Route represented differently (pair or string or dict)
    route_representation_type = random.choice(["pair","string","dict"])
    if route_representation_type == "pair":
        fields.append({"Identifier": rand_uuid(), "Index": 2, "ColIndex": 0, "Type": "pair",
                       "Label": "Route", "Value": [dep, arr], "Configuration": {"Name": "AT_ROUTE"}})
    elif route_representation_type == "string":
        fields.append({"Identifier": rand_uuid(), "Index": 2, "ColIndex": 0, "Type": "text",
                       "Label": "Route", "Value": f"{dep}-{arr}", "Configuration": {"Name": "AT_ROUTE"}})
    else:
        fields.append({"Identifier": rand_uuid(), "Index": 2, "ColIndex": 0, "Type": "object",
                       "Label": "Route", "Value": {"from": dep, "to": arr}, "Configuration": {"Name": "AT_ROUTE"}})

    # Aircraft sometimes nested, sometimes free text
    if rand_bool(0.6):
        fields.append({"Identifier": rand_uuid(), "Index": 3, "ColIndex": 0, "Type": "dropdown",
                       "Label": "Aircraft Type", "Value": random.choice(aircraft_at),
                       "Configuration": {"Name": "AT_AIRCRAFT", "Items": "\n".join(aircraft_at)}})
    else:
        fields.append({"Identifier": rand_uuid(), "Index": 3, "ColIndex": 0, "Type": "text",
                       "Label": "A/C", "Value": random.choice(aircraft_at), "Configuration": {"Name": "AT_AC_TXT"}})

    # Distance stored as km or nm or both, possibly under different keys
    dist_style = random.choice(["nm","km","both","missing"])
    if dist_style in ("nm","both"):
        fields.append({"Identifier": rand_uuid(), "Index": 4, "ColIndex": 0, "Type": "number",
                       "Label": "DistanceNM", "Value": str(nm), "Configuration": {"Name": "AT_DIST_NM"}})
    if dist_style in ("km","both"):
        fields.append({"Identifier": rand_uuid(), "Index": 5, "ColIndex": 0, "Type": "number",
                       "Label": "DistanceKM", "Value": str(km), "Configuration": {"Name": "AT_DIST_KM"}})

    # Autoland flag represented as checkbox or text
    if rand_bool(0.8):
        as_checkbox = rand_bool(0.5)
        if as_checkbox:
            fields.append({"Identifier": rand_uuid(), "Index": 6, "ColIndex": 0, "Type": "checkbox",
                           "Label": "Autoland", "Value": "true" if autoland else None, "Configuration": {"Name": "AT_AUTOLAND"}})
        else:
            fields.append({"Identifier": rand_uuid(), "Index": 6, "ColIndex": 0, "Type": "text",
                           "Label": "Autoland", "Value": "YES" if autoland else "NO", "Configuration": {"Name": "AT_AUTOLAND_TXT"}})

    # Add a grading block similar to sample (sometimes present)
    if rand_bool(0.6):
        fields.append({
            "Identifier": "00000000-0000-0000-0000-000000000000",
            "Index": 7, "ColIndex": 0, "Type": "overallgradecomp",
            "Label": "EBT grading:", "Value": None,
            "Values": [
                {"Key": rand_uuid(), "Value": str(random.randint(3,5))},
                {"Key": rand_uuid(), "Value": str(random.randint(3,5))},
                {"Key": rand_uuid(), "Value": str(random.randint(3,5))}
            ],
            "Configuration": {"Settings":[{"Name":"competencycomment","Value":"true"},{"Name":"showkpis","Value":"true"}]}
        })

    record = {
        "Airline": "AirTransat",
        "TrainingType": "Flight Training",
        "TemplateVersion": f"AT-FT-{i+1:02d}",
        "Date": rand_date(),
        "Type": "col1",
        "Fields": fields,
        "HasAssessmentFields": False
    }
    return record

# Create datasets
va_records = [make_virginair_record(i) for i in range(20)]
at_records = [make_airtransat_record(i) for i in range(20)]

# Save JSONL files

va_folder = base_dir / "virginair"
at_folder = base_dir / "airtransat"
va_folder.mkdir(exist_ok=True)
at_folder.mkdir(exist_ok=True)

# Save VirginAir records
for rec in va_records:
    filename = f"{rec['TemplateVersion']}.json"
    with (va_folder / filename).open("w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)

# Save AirTransat records
for rec in at_records:
    filename = f"{rec['TemplateVersion']}.json"
    with (at_folder / filename).open("w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
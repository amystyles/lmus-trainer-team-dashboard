"""
LMUS TAP Dashboard — Supabase Migration
Inserts team_members and bookings into Supabase.
Run AFTER executing schema.sql in the Supabase SQL Editor.
"""
import json, re, requests, sys
from datetime import datetime

SUPABASE_URL = "https://ptvzqqvbhrbophaotlnn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB0dnpxcXZiaHJib3BoYW90bG5uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc0MTU5ODMsImV4cCI6MjA5Mjk5MTk4M30.3YDiQKdUPGdjpSnsjUdNJ0brzCh8Lw27Bzk49Cu-7SI"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}

STATE_TO_REGION = {
    "WA":"West Coast","OR":"West Coast","CA":"West Coast","NV":"West Coast",
    "ID":"West Coast","AZ":"West Coast","UT":"West Coast","AK":"West Coast","HI":"West Coast",
    "NM":"South Central","TX":"South Central","OK":"South Central","AR":"South Central","LA":"South Central",
    "MT":"North Central","WY":"North Central","CO":"North Central","ND":"North Central",
    "SD":"North Central","NE":"North Central","IA":"North Central","MN":"North Central",
    "WI":"Midwest","MI":"Midwest","IL":"Midwest","IN":"Midwest","OH":"Midwest","MO":"Midwest","KS":"Midwest",
    "ME":"Mid East","NH":"Mid East","VT":"Mid East","MA":"Mid East","CT":"Mid East",
    "RI":"Mid East","NY":"Mid East","NJ":"Mid East","PA":"Mid East",
    "VA":"East Coast","NC":"East Coast","SC":"East Coast",
    "MD":"Mid Atlantic","DE":"Mid Atlantic","WV":"Mid Atlantic","DC":"Mid Atlantic",
    "FL":"Southeast","GA":"Southeast","AL":"Southeast","MS":"Southeast","TN":"Southeast","KY":"Southeast",
}

RC_NAMES = {
    "Karen Torrell","Sarah Gruba","Trae Tripoli","Dan Maroun",
    "Justine Collado","Jaime Terrell","Keri Ball","Stacy Dee Rathborne",
}
AT_NAMES = {
    "Andres Camargo","Andy Parrish","Ashley Lyon","Barb Knutson","Colleen King",
    "Dan Maroun","Jaime Terrell","Jen Parrish","Karen Torrell","Keri Ball",
    "Lauren Vibbert","Luca Callini","Mohamed Bounaim","Nikki Snow-Ybe","Sanna Ronkko",
    "Stacy Dee Rathborne","Sydnee Weinberg",
}

# ── TEAM MEMBERS ─────────────────────────────────────────────────
TRAINERS = [
    ("Alyx","Sparrow","alyx.sparrow@gmail.com","6360 W David Dr","Littleton","CO","80128"),
    ("Amy","Russo","amyrusso.lesmills@gmail.com","526 Bermuda Dr","Branchburg","NJ","8853"),
    ("Amy","Fisher","fisher.amyelizabeth@gmail.com","8105 Engelwood","Richland","MI","49083"),
    ("Ana","Malvaez","anamalvaez.lesmills@gmail.com","116 Quail Gardens Dr Apt 117","Encinitas","CA","92024"),
    ("Andres","Camargo","andres2camargo@gmail.com","3817 N OAK DR UNIT H31","Tampa","FL","33611"),
    ("Andrew","Aleman","aaaleman11@hotmail.com","4002 Via Lucero St #17","Santa Barbara","CA","93110"),
    ("Andy","Parrish","andy@andyparrish.com","3650 Dogwood Court","Lakeland","FL","33812"),
    ("Ann","McArthur","mcarthurann@yahoo.com","10108 Coronado Ave NE","Albuquerque","NM","87122"),
    ("Annette","Perkins","AnnettePerkins24@gmail.com","4033 N. New Land Loop","Lehi","UT","84043"),
    ("Ashley","McCallum","ashleymccallum84@gmail.com","13615 S. General Slocum Ct.","Fredericksburg","VA","22407"),
    ("Ashley","Lyon","ashley.lyon@doane.edu","2811 W Martell Road","Martell","NE","68404"),
    ("Barb","Knutson","bknutson513@hotmail.com","N164W20480 Currant Lane","Jackson","WI","53037"),
    ("Bethany","Entrekin","bethanyentrekin@gmail.com","202 Lauren LN","Canton","GA","30115"),
    ("Colleen","King","colleentolleking@gmail.com","1921 S Routt Ct","Lakewood","CO","80227"),
    ("Dan","Maroun","dmaroun2@illinois.edu","104 Denton Dr","Savoy","IL","61874"),
    ("Danielle","Kirk-Bagley","daniellebagley4@gmail.com","814 Whitby Ave","Yeadon","PA","19050"),
    ("Deidre","Douglas","dldwashington3@gmail.com","1077 Lambs Church Road","Altavista","VA","24517"),
    ("Elena","Kohler","elenadz@hotmail.com","11 Park valley CT","St Peters","MO","63376"),
    ("Hope","Bowie","hope2bfit@gmail.com","1409 Dearborn Rd.","Allen","TX","75002"),
    ("Jaime","Terrell","jaimeterrill7@gmail.com","1736 Havre De Grace Dr","Edgewater","MD","21037"),
    ("Jake","Pesquira","jake.pesquira@gmail.com","13 Goodwin Dr","North Brunswick","NJ","8902"),
    ("Jamila","Greene","milagreene1@hotmail.com","299 Shiloh Creek Dr","Calera","AL","35040"),
    ("Janice","Years","janiceyears@gmail.com","12826 Point Pleasant Drive","Fairfax","VA","22033"),
    ("Jen","Parrish","plata12583@yahoo.com","3650 Dogwood Court","Lakeland","FL","33812"),
    ("Jennifer","Pontarelli","jenpontarelli@comcast.net","1208 Walnut Ave","Voorhees","NJ","8043"),
    ("Jessica","Shallock","fellowshipfitness406@gmail.com","31237 Pineview Loop","Polson","MT","59860"),
    ("Jessica","Wong","jcw5070@gmail.com","50 Riverside Blvd Apt 8J","New York","NY","10069"),
    ("Judson","MacDonald","judsonwmac@gmail.com","600 Willard St, Unit 768","Durham","NC","27701"),
    ("Justine","Collado","pinacolada2525@yahoo.com","430 East McFarlan Street","Dover","NJ","7801"),
    ("Kamesha","Myers","kmyers81@gmail.com","900 Allan Road","Rockville","MD","20850"),
    ("Karen","Torrell","torrell.karen@gmail.com","2041 Via Mirada","Fullerton","CA","92833"),
    ("Katie","Kneupper","katiekneupper@live.com","12800 Center Lake Dr #223","Austin","TX","78753"),
    ("Keri","Ball","keriball.lesmills@gmail.com","1630 Trawler Lane","Annapolis","MD","21409"),
    ("Lauren","Hodoval","lahodoval@yahoo.com","6039 Eastbourne DR","Evansville","IN","47711"),
    ("Lauren","Vibbert","laurenfaith618@gmail.com","1211 Newport Ave","Lakeland","FL","33801"),
    ("Luca","Callini","lesmillsluca@gmail.com","2913 Sea Channel Drive","Seabrook","TX","77586"),
    ("Lucy","Xu","lxshopping@yahoo.com","3129 Dunsmmore Manor Ct","Spring","TX","77386"),
    ("Lula","Slaughter","lula.m.slaughter@gmail.com","6 Elwood Ave","Flemington","NJ","8822"),
    ("Marcus","Zomphier","mzomphi@gmail.com","7103 Kingsbury Circle","Tampa","FL","33610"),
    ("Megan","Cloe","meganmcloe@gmail.com","3484 Ashwood Ave","Los Angeles","CA","90066"),
    ("Melissa","Schimmel","mjmoore84@gmail.com","5673 Surfrider Way #103","Goleta","CA","93117"),
    ("Mohamed","Bounaim","m_bounaim1@yahoo.com","1207 Jungle Ave N","St Petersburg","FL","33710"),
    ("Nichola","Smiles","smiles.nichola@gmail.com","7530 Summer Night Lane","Richmond","TX","77469"),
    ("Nicholas","Castro","nacastro928@gmail.com","8832 Joyzelle Dr.","Garden Grove","CA","92841"),
    ("Nikki","Snow-Ybe","nikkisnow921@gmail.com","4601 N Ravenswood Ave Unit 202","Chicago","IL","60640"),
    ("Paula","Thomas","paulathomasfitness@gmail.com","430 Scotts Way","Augusta","GA","30909"),
    ("Robin","Oh","roboh.lesmills@gmail.com","495 Grand View Ave Apt 7","San Francisco","CA","94114"),
    ("Sanna","Ronkko","sannathefit@hotmail.com","2116 South Sycamore Str","Santa Ana","CA","92707"),
    ("Sara","Green","sarahalley2019@gmail.com","6619 East Lowry Blvd #307","Denver","CO","80230"),
    ("Sarah","Gruba","SarahG@ambitionathletics.co","8211 Water Breeze Drive","Magnolia","TX","77354"),
    ("Shelby","Schrader","shelbyschrader@hotmail.com","1476 East Tierra Street","Gilbert","AZ","85297"),
    ("Stacy Dee","Rathborne","StacyDee1214@aol.com","1480 Hammock Ridge Rd, Apt 13303","Clermont","FL","34711"),
    ("Sydnee","Weinberg","sydneew91@gmail.com","32 Reler Lane, Apt E","Somerset","NJ","8873"),
    ("Trae","Tripoli","traetripoli@gmail.com","559 West Saddle Dr.","Grand Junction","CO","81507"),
    ("Vivian","Gill","vivian.j.gill@gmail.com","162 Willow Bend Dr","Hendersonville","TN","37075"),
    ("Will","Lee","wlee1989@gmail.com","15829 Begonia Ave","Chino","CA","94582"),
]

ASSESSORS = [
    ("Alexa","Nikoloff","","30 Ashton Street","Carlisle","PA","17015"),
    ("Alison","Poole","","1031 Penn Grant Rd","Lancaster","PA","17602"),
    ("Amelia","Luchey","","808 Union Ave","Baltimore","MD","21211"),
    ("Cara","Leisnham","","6B Hillside Rd","Greenbelt","MD","20770"),
    ("Gladyss","Saenz","","5806 Nolan Ryan Dr","Midland","TX","79706"),
    ("Jessica","Clevenger","","7940 Poplar Creek Road","Nashville","TN","37221"),
    ("Heather","Biddle","","640 Wild Horse Ln","Brandon","MS","39042"),
    # Add remaining 3 assessors here when available:
    # ("First","Last","email","address","city","ST","zip"),
]

def build_member(first, last, email, address, city, state, zip_code, role):
    state = state.upper().strip()
    region = STATE_TO_REGION.get(state, "Unknown")
    full_name = f"{first} {last}"
    # Special case: Stacy Dee Rathborne full_name override
    if first == "Stacy Dee":
        full_name = "Stacy Dee Rathborne"
    return {
        "first_name": first,
        "last_name": last,
        "full_name": full_name,
        "email": email,
        "address": address,
        "city": city,
        "state": state,
        "zip": zip_code,
        "home_region": region,
        "role": role,
        "is_rc": full_name in RC_NAMES,
        "is_at": full_name in AT_NAMES,
        "is_dt": False,
    }

def upsert(table, rows, chunk=50):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    total = 0
    for i in range(0, len(rows), chunk):
        batch = rows[i:i+chunk]
        r = requests.post(url, headers=HEADERS, json=batch)
        if r.status_code not in (200, 201):
            print(f"  ERROR {r.status_code}: {r.text[:200]}")
            sys.exit(1)
        total += len(batch)
        print(f"  ✓ {table}: {total}/{len(rows)}")

def parse_bookings():
    path = "/Users/amy.styles/Documents/lmus-trainer-team-dashboard/bookings-data.js"
    with open(path) as f:
        src = f.read()
    raw = re.search(r'var BOOKINGS\s*=\s*(\[.*?\]);', src, re.DOTALL)
    if not raw:
        print("Could not parse bookings-data.js"); sys.exit(1)
    data = json.loads(raw.group(1))
    rows = []
    for b in data:
        try:
            sd = datetime.strptime(b["startDate"], "%m/%d/%Y").date().isoformat()
        except Exception:
            sd = None
        rows.append({
            "event":          b.get("event"),
            "booking_id":     b.get("bookingId"),
            "trainer":        b.get("trainer"),
            "event_type":     b.get("eventType"),
            "program":        b.get("program"),
            "start_date":     sd,
            "region":         b.get("region"),
            "is_online":      bool(b.get("isOnline", False)),
            "fiscal_year":    b.get("fiscalYear"),
            "fiscal_quarter": b.get("fiscalQuarter"),
            "status":         b.get("status"),
            "confirmed":      bool(b.get("confirmed", False)),
            "dual_group":     b.get("dualGroup"),
        })
    return rows

def main():
    print("── Team Members ─────────────────────────────")
    members = []
    for t in TRAINERS:
        members.append(build_member(*t, "Trainer"))
    for a in ASSESSORS:
        members.append(build_member(*a, "Assessor"))
    upsert("team_members", members)

    print("\n── Bookings ──────────────────────────────────")
    bookings = parse_bookings()
    print(f"  Parsed {len(bookings)} bookings from bookings-data.js")
    upsert("bookings", bookings)

    print("\n✅ Migration complete.")

if __name__ == "__main__":
    main()

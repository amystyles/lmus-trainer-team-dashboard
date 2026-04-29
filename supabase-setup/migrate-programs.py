"""
LMUS TAP — Programs Migration
Reads 'TAP Team 2026 Updated .xlsx' and upserts the programs JSONB field
on every team_member row. Run AFTER add-programs-column.sql.

Usage:
  python3 supabase-setup/migrate-programs.py
"""
import json, requests, sys
import pandas as pd

SUPABASE_URL = "https://ptvzqqvbhrbophaotlnn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB0dnpxcXZiaHJib3BoYW90bG5uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc0MTU5ODMsImV4cCI6MjA5Mjk5MTk4M30.3YDiQKdUPGdjpSnsjUdNJ0brzCh8Lw27Bzk49Cu-7SI"
EXCEL_PATH   = "/Users/amy.styles/Desktop/TAP Team 2026 Updated .xlsx"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

# Assessor sheet uses different column names for some programs
ASSESSOR_COL_MAP = {
    "CEREMONY": "CER",
    "CORE":     "COR",
    "GRIT":     "GR",
    "PILATES":  "PL",
    "TONE":     "TON",
    "SPRINT":   "SP",
}

# Excel name → canonical Supabase full_name
NAME_FIXES = {
    "Dani Kirk-Bagley":     "Danielle Kirk-Bagley",
    "Jaime Terrill":        "Jaime Terrell",
    "Stacy Dee Rathbone":   "Stacy Dee Rathborne",
    "Jessica Schallock":    "Jessica Shallock",
    "Nick Castro":          "Nicholas Castro",
    "Ana Malváez":          "Ana Malvaez",
    "Kristin Strickland":   "Kristen Strickland",
    "Nadia Hassan":         "Nadia Hasan",
    "Nicci Hockenberry":    "Nicci Hoickenberry",
    "Jen Pontarelli":       "Jennifer Pontarelli",
}

def normalize(name):
    import unicodedata
    return unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode().lower().strip()

def parse_trainer_sheet(xl):
    df = xl.parse("Trainer Roles by Program").fillna("")
    result = {}
    prog_cols = [c for c in df.columns if c != "Trainer"]
    for _, row in df.iterrows():
        name = str(row["Trainer"]).strip()
        if not name:
            continue
        progs = {col: str(row[col]).strip() for col in prog_cols if str(row[col]).strip()}
        result[name] = progs
    return result

def parse_assessor_sheet(xl):
    df = xl.parse("Assessor Roles by Program").fillna("")
    result = {}
    prog_cols = [c for c in df.columns if c != "Assessor"]
    for _, row in df.iterrows():
        name = str(row["Assessor"]).strip()
        if not name:
            continue
        progs = {}
        for col in prog_cols:
            val = str(row[col]).strip()
            if not val:
                continue
            code = ASSESSOR_COL_MAP.get(col, col)
            progs[code] = val
        result[name] = progs
    return result

def fetch_db_names():
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/team_members?select=full_name&limit=500",
        headers=HEADERS,
    )
    if r.status_code != 200:
        print(f"ERROR fetching team members: {r.status_code} {r.text[:200]}")
        sys.exit(1)
    return {m["full_name"] for m in r.json()}

def build_combined(trainer_map, assessor_map):
    combined = {}
    all_names = set(trainer_map) | set(assessor_map)
    for name in all_names:
        t = trainer_map.get(name, {})
        a = assessor_map.get(name, {})
        merged = {**a, **t}  # trainer sheet wins on overlap
        combined[name] = merged
    return combined

def upsert_programs(db_names, combined, norm_to_db):
    skipped = []
    patched = 0
    for excel_name, progs in combined.items():
        canonical = NAME_FIXES.get(excel_name, excel_name)
        if canonical not in db_names:
            # try normalized fallback
            canonical = norm_to_db.get(normalize(excel_name))
        if not canonical:
            skipped.append(excel_name)
            continue
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/team_members?full_name=eq.{requests.utils.quote(canonical)}",
            headers=HEADERS,
            json={"programs": progs},
        )
        if r.status_code not in (200, 204):
            print(f"  ERROR {canonical}: {r.status_code} {r.text[:200]}")
        else:
            print(f"  ✓ {canonical}: {len(progs)} programs")
            patched += 1
    return patched, skipped

def main():
    xl = pd.ExcelFile(EXCEL_PATH)

    print("── Parsing Excel ─────────────────────────────")
    trainer_map  = parse_trainer_sheet(xl)
    assessor_map = parse_assessor_sheet(xl)
    combined     = build_combined(trainer_map, assessor_map)
    print(f"  {len(combined)} unique people found in Excel")

    print("\n── Fetching DB names ─────────────────────────")
    db_names   = fetch_db_names()
    norm_to_db = {normalize(n): n for n in db_names}
    print(f"  {len(db_names)} team members in Supabase")

    print("\n── Upserting programs ────────────────────────")
    patched, skipped = upsert_programs(db_names, combined, norm_to_db)

    print(f"\n✅ Done — {patched} updated")
    if skipped:
        print(f"⚠️  Not found in DB ({len(skipped)}): {', '.join(skipped)}")

if __name__ == "__main__":
    main()

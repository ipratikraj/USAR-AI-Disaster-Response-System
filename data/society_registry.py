"""
Society Resident Registry and Disaster Evacuation Roster Data Layer.
Provides 100% offline SQLite persistence for Green Valley Residency.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import io

DB_PATH = Path(__file__).resolve().parent / "society_registry.db"

VULNERABILITY_OPTIONS = [
    "None (Able-bodied)",
    "♿ Wheelchair / Mobility Impaired",
    "👴 Elderly Alone (>75 yrs)",
    "🫁 Bedridden / Oxygen / Medical Support",
    "👶 Infant / Toddler (<2 yrs)",
    "🩺 Cardiac / Chronic Condition"
]

PET_OPTIONS = [
    "None",
    "🐕 Dog",
    "🐈 Cat",
    "🐕 2 Dogs",
    "🐈 2 Cats",
    "🐕 Dog + 🐈 Cat",
    "🐾 Other Small Pet"
]

EVACUATION_STATUSES = {
    "SAFE_AT_ASSEMBLY": ("🟢 Safe at Assembly Lawn", "#2ea043"),
    "UNACCOUNTED": ("⚪ Unaccounted / Missing", "#8b949e"),
    "CONFIRMED_TRAPPED": ("🔴 Confirmed Trapped (AI/Acoustic)", "#ff3366"),
    "OFF_SITE": ("🟡 Away / Off-Site", "#d29922")
}

def get_connection():
    """Returns a connection with Row factory enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_reseed: bool = False):
    """Initializes tables and populates with realistic seed data if empty."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if force_reseed:
        cursor.execute("DROP TABLE IF EXISTS residents")
        
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS residents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tower_id TEXT NOT NULL,
        flat_number TEXT NOT NULL,
        floor INTEGER NOT NULL,
        primary_resident TEXT NOT NULL,
        phone TEXT NOT NULL,
        occupants_count INTEGER NOT NULL DEFAULT 1,
        vulnerability TEXT NOT NULL DEFAULT 'None (Able-bodied)',
        pets TEXT NOT NULL DEFAULT 'None',
        emergency_contact_name TEXT,
        emergency_contact_phone TEXT,
        evacuation_status TEXT NOT NULL DEFAULT 'UNACCOUNTED',
        notes TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(tower_id, flat_number)
    )
    """)
    conn.commit()
    
    # Check if empty, seed initial data
    cursor.execute("SELECT COUNT(*) FROM residents")
    count = cursor.fetchone()[0]
    
    if count == 0:
        seed_data = [
            # Tower A
            ("Tower A", "A-101", 1, "Major Vikram Rao (Retd.)", "+91 98201 11001", 2, "👴 Elderly Alone (>75 yrs)", "🐕 Dog (Labrador)", "Capt. Rahul Rao (Son)", "+91 98201 99001", "UNACCOUNTED", "Ground floor, wooden door. Hearing aid user."),
            ("Tower A", "A-102", 1, "Priya & Sandeep Nair", "+91 98201 11002", 4, "👶 Infant / Toddler (<2 yrs)", "None", "Mrs. Leela Nair", "+91 98201 99002", "SAFE_AT_ASSEMBLY", "Has 8-month-old infant. Evacuated safely with stroller."),
            ("Tower A", "A-201", 2, "Dr. Arvind Mehta", "+91 98201 11003", 3, "None (Able-bodied)", "None", "Suresh Mehta", "+91 98201 99003", "SAFE_AT_ASSEMBLY", "Doctor; currently assisting at first-aid triage tent."),
            ("Tower A", "A-202", 2, "Sunita & Alok Sharma", "+91 98201 11004", 4, "None (Able-bodied)", "🐈 Cat (Persian)", "Kavita Sharma", "+91 98201 99004", "UNACCOUNTED", "White Persian cat inside flat."),
            ("Tower A", "A-301", 3, "Harishchandra Joshi", "+91 98201 11005", 1, "🫁 Bedridden / Oxygen / Medical Support", "None", "Gaurav Joshi (Son)", "+91 98201 99005", "CONFIRMED_TRAPPED", "Requires active home oxygen concentrator. Stretcher squad dispatched."),
            ("Tower A", "A-401", 4, "Deepak & Neha Verma", "+91 98201 11006", 3, "None (Able-bodied)", "🐕 Dog", "Ramesh Verma", "+91 98201 99006", "UNACCOUNTED", "Pet dog inside."),
            
            # Tower B
            ("Tower B", "B-101", 1, "Gurpreet & Jasleen Singh", "+91 98202 22001", 5, "None (Able-bodied)", "🐕 Dog", "Maninder Singh", "+91 98202 99001", "SAFE_AT_ASSEMBLY", "Family of 5 accounted for at lawn."),
            ("Tower B", "B-201", 2, "Kalyani & S. Venkataraman", "+91 98202 22002", 2, "👴 Elderly Alone (>75 yrs)", "None", "Dr. Karthik Venkat (US)", "+1 415 555 0192", "UNACCOUNTED", "Both aged 81 and 78. Very slow walking pace."),
            ("Tower B", "B-202", 2, "Ananya & Rohan Iyer", "+91 98202 22003", 2, "None (Able-bodied)", "🐈 Cat", "S. Iyer", "+91 98202 99003", "SAFE_AT_ASSEMBLY", "Both safe on the lawn."),
            ("Tower B", "B-301", 3, "Mahesh Kulkarni", "+91 98202 22004", 2, "♿ Wheelchair / Mobility Impaired", "None", "Swapnil Kulkarni", "+91 98202 99004", "UNACCOUNTED", "Paraplegic resident. Cannot use staircases without evacuation chair."),
            ("Tower B", "B-302", 3, "Rajesh & Meena Gupta", "+91 98202 22005", 4, "None (Able-bodied)", "None", "Ashok Gupta", "+91 98202 99005", "SAFE_AT_ASSEMBLY", "Safe at assembly point."),
            ("Tower B", "B-401", 4, "Amitabh & Ritu Sen", "+91 98202 22006", 3, "None (Able-bodied)", "🐕 Dog", "Debashis Sen", "+91 98202 99006", "UNACCOUNTED", "Spotted near balcony by aerial drone."),

            # Tower C
            ("Tower C", "C-101", 1, "George & Mary Fernandez", "+91 98203 33001", 2, "👴 Elderly Alone (>75 yrs)", "🐕 Dog", "Paul Fernandez", "+91 98203 99001", "SAFE_AT_ASSEMBLY", "Ground floor evacuated promptly."),
            ("Tower C", "C-102", 1, "Vikas & Pooja Malhotra", "+91 98203 33002", 3, "👶 Infant / Toddler (<2 yrs)", "None", "R. K. Malhotra", "+91 98203 99002", "SAFE_AT_ASSEMBLY", "Safe at gate lawn."),
            ("Tower C", "C-201", 2, "Farhan & Shagufta Ali", "+91 98203 33003", 4, "None (Able-bodied)", "None", "Zaid Ali", "+91 98203 99003", "UNACCOUNTED", "Flat locked from outside."),
            ("Tower C", "C-301", 3, "Mrs. Kamla Devi", "+91 98203 33004", 1, "👴 Elderly Alone (>75 yrs)", "None", "Subhash (Nephew)", "+91 98203 99004", "CONFIRMED_TRAPPED", "Trapped in bathroom behind jammed frame. Rescue team en route."),
            ("Tower C", "C-401", 4, "Naveen & Swati Reddy", "+91 98203 33005", 4, "None (Able-bodied)", "🐈 2 Cats", "K. Reddy", "+91 98203 99005", "SAFE_AT_ASSEMBLY", "Reported 2 indoor cats still inside flat."),
            ("Tower C", "C-501", 5, "Siddharth Chatterjee", "+91 98203 33006", 1, "None (Able-bodied)", "None", "M. Chatterjee", "+91 98203 99006", "OFF_SITE", "Out of station in Bengaluru on business trip."),

            # Tower D
            ("Tower D", "D-101", 1, "Dinesh & Usha Patel", "+91 98204 44001", 4, "None (Able-bodied)", "None", "Bhavin Patel", "+91 98204 99001", "SAFE_AT_ASSEMBLY", "Safe at community lawn."),
            ("Tower D", "D-102", 1, "B. R. Deshmukh", "+91 98204 44002", 2, "♿ Wheelchair / Mobility Impaired", "None", "Amol Deshmukh", "+91 98204 99002", "SAFE_AT_ASSEMBLY", "Ground floor wheelchair ramp allowed rapid self-evacuation."),
            ("Tower D", "D-201", 2, "Tarun & Shalini Khurana", "+91 98204 44003", 3, "None (Able-bodied)", "🐕 Dog", "Vipin Khurana", "+91 98204 99003", "UNACCOUNTED", "Dog barking heard on 2nd floor corridor."),
            ("Tower D", "D-202", 2, "Rituja & Sameer Deshpande", "+91 98204 44004", 2, "None (Able-bodied)", "🐈 Cat", "S. Deshpande", "+91 98204 99004", "SAFE_AT_ASSEMBLY", "Safe at assembly point."),
            ("Tower D", "D-301", 3, "Manish & Shweta Bhatia", "+91 98204 44005", 4, "👶 Infant / Toddler (<2 yrs)", "None", "Prem Bhatia", "+91 98204 99005", "UNACCOUNTED", "Awaiting confirmation from Tower D staircase squad."),
            ("Tower D", "D-401", 4, "Col. Balbir Chib (Retd.)", "+91 98204 44006", 2, "🩺 Cardiac / Chronic Condition", "🐕 Dog", "Capt. K. Chib", "+91 98204 99006", "UNACCOUNTED", "Cardiac patient; elevator inoperable.")
        ]
        
        cursor.executemany("""
        INSERT INTO residents (
            tower_id, flat_number, floor, primary_resident, phone, occupants_count,
            vulnerability, pets, emergency_contact_name, emergency_contact_phone,
            evacuation_status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_data)
        conn.commit()
        
    conn.close()

def get_headcount_stats():
    """
    Computes life-safety reconciliation stats across all flats:
    Total, Safe at Assembly, Confirmed Trapped, Unaccounted, High-Vulnerability Unaccounted, Pets Count.
    """
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM residents", conn)
    conn.close()
    
    total_flats = len(df)
    total_residents = int(df["occupants_count"].sum()) if not df.empty else 0
    
    safe_flats = len(df[df["evacuation_status"] == "SAFE_AT_ASSEMBLY"])
    safe_residents = int(df[df["evacuation_status"] == "SAFE_AT_ASSEMBLY"]["occupants_count"].sum()) if not df.empty else 0
    
    trapped_flats = len(df[df["evacuation_status"] == "CONFIRMED_TRAPPED"])
    trapped_residents = int(df[df["evacuation_status"] == "CONFIRMED_TRAPPED"]["occupants_count"].sum()) if not df.empty else 0
    
    offsite_flats = len(df[df["evacuation_status"] == "OFF_SITE"])
    offsite_residents = int(df[df["evacuation_status"] == "OFF_SITE"]["occupants_count"].sum()) if not df.empty else 0
    
    unaccounted_flats = len(df[df["evacuation_status"] == "UNACCOUNTED"])
    unaccounted_residents = int(df[df["evacuation_status"] == "UNACCOUNTED"]["occupants_count"].sum()) if not df.empty else 0
    
    # Critical vulnerable residents who are not yet safe
    vulnerable_unaccounted = df[
        (df["evacuation_status"].isin(["UNACCOUNTED", "CONFIRMED_TRAPPED"])) & 
        (df["vulnerability"] != "None (Able-bodied)")
    ]
    vuln_unaccounted_flats = len(vulnerable_unaccounted)
    vuln_unaccounted_residents = int(vulnerable_unaccounted["occupants_count"].sum()) if not vulnerable_unaccounted.empty else 0
    
    # Pets still inside
    pets_inside_flats = len(df[
        (df["evacuation_status"].isin(["UNACCOUNTED", "CONFIRMED_TRAPPED"])) & 
        (df["pets"] != "None")
    ])
    
    return {
        "total_flats": total_flats,
        "total_residents": total_residents,
        "safe_flats": safe_flats,
        "safe_residents": safe_residents,
        "trapped_flats": trapped_flats,
        "trapped_residents": trapped_residents,
        "offsite_flats": offsite_flats,
        "offsite_residents": offsite_residents,
        "unaccounted_flats": unaccounted_flats,
        "unaccounted_residents": unaccounted_residents,
        "vuln_unaccounted_flats": vuln_unaccounted_flats,
        "vuln_unaccounted_residents": vuln_unaccounted_residents,
        "pets_inside_flats": pets_inside_flats
    }

def get_all_residents(tower=None, status=None, only_vulnerable=False, search_query=None):
    """Retrieves filtered list of residents as a pandas DataFrame."""
    init_db()
    conn = get_connection()
    
    query = "SELECT * FROM residents WHERE 1=1"
    params = []
    
    if tower and tower != "All Towers":
        query += " AND tower_id = ?"
        params.append(tower)
        
    if status and status != "All Statuses":
        query += " AND evacuation_status = ?"
        params.append(status)
        
    if only_vulnerable:
        query += " AND vulnerability != 'None (Able-bodied)'"
        
    if search_query:
        query += " AND (flat_number LIKE ? OR primary_resident LIKE ? OR phone LIKE ?)"
        term = f"%{search_query.strip()}%"
        params.extend([term, term, term])
        
    query += " ORDER BY tower_id ASC, floor ASC, flat_number ASC"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def update_resident_status(resident_id: int, new_status: str):
    """Updates evacuation status for a given resident."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE residents 
    SET evacuation_status = ?, last_updated = CURRENT_TIMESTAMP 
    WHERE id = ?
    """, (new_status, resident_id))
    conn.commit()
    conn.close()

def add_resident(tower_id, flat_number, floor, primary_resident, phone, occupants_count,
                 vulnerability, pets, emergency_contact_name, emergency_contact_phone,
                 evacuation_status="UNACCOUNTED", notes=""):
    """Inserts a new resident flat record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO residents (
        tower_id, flat_number, floor, primary_resident, phone, occupants_count,
        vulnerability, pets, emergency_contact_name, emergency_contact_phone,
        evacuation_status, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (tower_id, flat_number, floor, primary_resident, phone, occupants_count,
          vulnerability, pets, emergency_contact_name, emergency_contact_phone,
          evacuation_status, notes))
    conn.commit()
    conn.close()

def update_resident(resident_id, tower_id, flat_number, floor, primary_resident, phone,
                    occupants_count, vulnerability, pets, emergency_contact_name,
                    emergency_contact_phone, evacuation_status, notes):
    """Updates an existing resident flat record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE residents SET
        tower_id = ?, flat_number = ?, floor = ?, primary_resident = ?, phone = ?,
        occupants_count = ?, vulnerability = ?, pets = ?, emergency_contact_name = ?,
        emergency_contact_phone = ?, evacuation_status = ?, notes = ?, last_updated = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (tower_id, flat_number, floor, primary_resident, phone, occupants_count,
          vulnerability, pets, emergency_contact_name, emergency_contact_phone,
          evacuation_status, notes, resident_id))
    conn.commit()
    conn.close()

def delete_resident(resident_id: int):
    """Deletes a resident record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM residents WHERE id = ?", (resident_id,))
    conn.commit()
    conn.close()

def get_residents_by_sector(tower_id: str, floor_min: int = 1, floor_max: int = 10):
    """Finds all residents in a specific tower and floor range (used for AI sector linking)."""
    init_db()
    conn = get_connection()
    query = """
    SELECT * FROM residents 
    WHERE tower_id = ? AND floor >= ? AND floor <= ?
    ORDER BY floor ASC, flat_number ASC
    """
    df = pd.read_sql_query(query, conn, params=[tower_id, floor_min, floor_max])
    conn.close()
    return df

def export_to_csv() -> str:
    """Exports full registry to CSV string for backup/download."""
    df = get_all_residents()
    return df.to_csv(index=False)

def import_from_csv(csv_content: str) -> tuple[int, str]:
    """Imports or updates residents from CSV string. Returns (imported_count, error_msg)."""
    try:
        df = pd.read_csv(io.StringIO(csv_content))
        required_cols = {"tower_id", "flat_number", "floor", "primary_resident", "phone", "occupants_count"}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            return 0, f"CSV missing required columns: {', '.join(missing)}"
        
        conn = get_connection()
        cursor = conn.cursor()
        count = 0
        for _, row in df.iterrows():
            cursor.execute("""
            INSERT INTO residents (
                tower_id, flat_number, floor, primary_resident, phone, occupants_count,
                vulnerability, pets, emergency_contact_name, emergency_contact_phone,
                evacuation_status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(tower_id, flat_number) DO UPDATE SET
                floor = excluded.floor,
                primary_resident = excluded.primary_resident,
                phone = excluded.phone,
                occupants_count = excluded.occupants_count,
                vulnerability = excluded.vulnerability,
                pets = excluded.pets,
                emergency_contact_name = excluded.emergency_contact_name,
                emergency_contact_phone = excluded.emergency_contact_phone,
                evacuation_status = excluded.evacuation_status,
                notes = excluded.notes,
                last_updated = CURRENT_TIMESTAMP
            """, (
                str(row.get("tower_id", "Tower A")),
                str(row.get("flat_number", "")),
                int(row.get("floor", 1)),
                str(row.get("primary_resident", "Unknown")),
                str(row.get("phone", "")),
                int(row.get("occupants_count", 1)),
                str(row.get("vulnerability", "None (Able-bodied)")),
                str(row.get("pets", "None")),
                str(row.get("emergency_contact_name", "")),
                str(row.get("emergency_contact_phone", "")),
                str(row.get("evacuation_status", "UNACCOUNTED")),
                str(row.get("notes", ""))
            ))
            count += 1
        conn.commit()
        conn.close()
        return count, ""
    except Exception as e:
        return 0, str(e)

if __name__ == "__main__":
    init_db(force_reseed=True)
    stats = get_headcount_stats()
    print("Database initialized successfully!")
    print(f"Total Flats: {stats['total_flats']} | Total Residents: {stats['total_residents']}")
    print(f"Safe: {stats['safe_residents']} | Trapped: {stats['trapped_residents']} | Unaccounted: {stats['unaccounted_residents']}")
    print(f"High-Vulnerability Unaccounted Flats: {stats['vuln_unaccounted_flats']}")

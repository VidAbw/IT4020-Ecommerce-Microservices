import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DBS = {
    "users": ROOT / "user-service" / "users.db",
    "products": ROOT / "product-service" / "products.db",
    "cart": ROOT / "cart-service" / "cart.db",
    "orders": ROOT / "order-service" / "orders.db",
    "inventory": ROOT / "inventory-service" / "inventory.db",
    "payments": ROOT / "payment-service" / "payments.db",
}


def inspect_db(service: str, db_path: Path) -> None:
    print(f"\n[{service}] {db_path}")
    if not db_path.exists():
        print("  - MISSING")
        return

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = [row[0] for row in cur.fetchall()]

        if not tables:
            print("  - No user tables found")
            return

        for table in tables:
            count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  - {table}: {count} rows")
    finally:
        conn.close()


if __name__ == "__main__":
    print("SQLite Database Inspection")
    for svc, path in DBS.items():
        inspect_db(svc, path)

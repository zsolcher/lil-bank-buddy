import pandas as pd
import sqlite3
import os

# File paths
DB_PATH = 'data/usaa_transactions.db'
EXPORT_DIR = 'data/bank-exports/'
CSV_TABLES = {
    'team-beeb-cc_02-01-2025_07_01_2025.csv': 'team_beeb_cc',
    'team-beeb-checking_01-01-2025_07_01_2025.csv': 'team_beeb_checking',
}

# Column mapping from CSV to DB
COLUMN_MAP = {
    'Date': 'date',
    'Description': 'description',
    'Original Description': 'original_description',
    'Category': 'category',
    'Amount': 'amount',
    'Status': 'status',
}

def import_csv_to_sqlite():
    conn = sqlite3.connect(DB_PATH)
    for csv_file, table in CSV_TABLES.items():
        csv_path = os.path.join(EXPORT_DIR, csv_file)
        df = pd.read_csv(csv_path)
        # Rename columns to match DB schema
        df = df.rename(columns=COLUMN_MAP)
        # Only keep columns that match DB schema
        df = df[list(COLUMN_MAP.values())]
        # Import to SQLite (auto-increment id will be handled by DB)
        df.to_sql(table, conn, if_exists='append', index=False)
        print(f"Imported {len(df)} rows from {csv_file} into {table}")
    conn.close()

if __name__ == '__main__':
    import_csv_to_sqlite()

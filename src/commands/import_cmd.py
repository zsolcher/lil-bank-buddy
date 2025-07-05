"""Import command for importing CSV files into the database."""
import click
import pandas as pd
import os
from ..core.database import DatabaseManager

# Default configuration
DEFAULT_EXPORT_DIR = 'data/bank-exports/'
DEFAULT_CSV_TABLES = {
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

@click.command()
@click.option('--export-dir', default=DEFAULT_EXPORT_DIR, 
              help='Directory containing CSV export files')
@click.option('--db-path', default=None,
              help='Path to SQLite database (uses default if not specified)')
@click.option('--dry-run', is_flag=True,
              help='Show what would be imported without actually importing')
def import_cmd(export_dir, db_path, dry_run):
    """Import CSV files from bank exports into the database."""
    db_manager = DatabaseManager(db_path) if db_path else DatabaseManager()
    
    # Check if export directory exists
    if not os.path.exists(export_dir):
        click.echo(f"Error: Export directory '{export_dir}' not found.")
        return
    
    # Find CSV files in directory
    csv_files = [f for f in os.listdir(export_dir) if f.endswith('.csv')]
    
    if not csv_files:
        click.echo(f"No CSV files found in '{export_dir}'")
        return
    
    click.echo(f"Found {len(csv_files)} CSV files in '{export_dir}':")
    for csv_file in csv_files:
        click.echo(f"  - {csv_file}")
    
    if dry_run:
        click.echo("\n[DRY RUN] Would import the following:")
        for csv_file in csv_files:
            csv_path = os.path.join(export_dir, csv_file)
            try:
                df = pd.read_csv(csv_path)
                table_name = DEFAULT_CSV_TABLES.get(csv_file, 
                    csv_file.replace('.csv', '').replace('-', '_'))
                click.echo(f"  - {csv_file} → {table_name} ({len(df)} rows)")
            except Exception as e:
                click.echo(f"  - {csv_file} → ERROR: {e}")
        return
    
    # Import files
    total_imported = 0
    for csv_file in csv_files:
        csv_path = os.path.join(export_dir, csv_file)
        table_name = DEFAULT_CSV_TABLES.get(csv_file, 
            csv_file.replace('.csv', '').replace('-', '_'))
        
        try:
            df = pd.read_csv(csv_path)
            
            # Rename columns to match DB schema
            df = df.rename(columns=COLUMN_MAP)
            
            # Only keep columns that match DB schema
            available_columns = [col for col in COLUMN_MAP.values() if col in df.columns]
            df = df[available_columns]
            
            # Import to SQLite
            rows_imported = db_manager.import_dataframe(df, table_name)
            click.echo(f"✓ Imported {rows_imported} rows from {csv_file} into {table_name}")
            total_imported += rows_imported
            
        except Exception as e:
            click.echo(f"✗ Error importing {csv_file}: {e}")
    
    click.echo(f"\nTotal rows imported: {total_imported}")

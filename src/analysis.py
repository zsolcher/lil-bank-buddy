# analysis.py
import pandas as pd
from db_utils import get_connection

def format_dollar(amount):
    return f"${amount:,.2f}"

def get_account_summary(table_name):
    with get_connection() as conn:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    summary = {
        'total_transactions': len(df),
        'total_amount': format_dollar(df['amount'].sum()),
        'largest_transaction': format_dollar(df['amount'].max()),
        'smallest_transaction': format_dollar(df['amount'].min()),
        'date_range': (df['date'].min(), df['date'].max()),
        'most_frequent_category': df['category'].mode()[0] if not df['category'].isnull().all() else None,
    }
    return summary

def get_recent_activity(table_name, days=30):
    with get_connection() as conn:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    df['date'] = pd.to_datetime(df['date'])
    recent = df[df['date'] >= pd.Timestamp.now() - pd.Timedelta(days=days)]
    return {
        'num_transactions': len(recent),
        'total_amount': format_dollar(recent['amount'].sum()),
        'top_categories': recent['category'].value_counts().head(3).to_dict(),
    }

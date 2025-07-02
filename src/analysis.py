# analysis.py
import pandas as pd
from .db_utils import get_connection

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

def find_last_settlement_date(df):
    """
    Intelligently find the last settlement date by looking for payment patterns.
    
    Looks for:
    1. Multiple credit card payments within a few days
    2. Excludes automated rewards payments (~$50)
    3. Returns the date of the most recent payment in a settlement cycle
    
    Args:
        df: DataFrame with transaction data, sorted by date descending
    
    Returns:
        Last settlement date or None if no pattern found
    """
    # Look for credit card payments (negative amounts with "CREDIT CARD PAYMENT" or similar)
    payments = df[
        (df['amount'] < 0) & 
        (df['description'].str.contains('CREDIT CARD PAYMENT|Payment', case=False, na=False))
    ].copy()
    
    if len(payments) == 0:
        return None
    
    # Sort by date descending to get most recent first
    payments = payments.sort_values('date', ascending=False)
    
    # Look for multiple payments within a reasonable settlement window (30 days)
    most_recent_payment = payments.iloc[0]
    most_recent_date = most_recent_payment['date']
    
    # Look for other payments within 30 days before this one
    settlement_window_start = most_recent_date - pd.Timedelta(days=30)
    payments_in_window = payments[
        (payments['date'] >= settlement_window_start) & 
        (payments['date'] <= most_recent_date)
    ]
    
    if len(payments_in_window) >= 2:
        # Multiple payments found - return the most recent one
        return most_recent_date
    else:
        # Single payment - still use it as settlement date
        return most_recent_date

def analyze_payment_patterns(table_name):
    """
    Analyze payment patterns to identify individual contributors.
    
    Returns:
        Dictionary with payment analysis
    """
    with get_connection() as conn:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date', ascending=False)
    
    # Find credit card payments
    payments = df[
        (df['amount'] < 0) & 
        (df['description'].str.contains('CREDIT CARD PAYMENT', case=False, na=False))
    ].copy()
    
    if len(payments) == 0:
        return {
            'recent_payments': [],
            'total_recent_payments': 0,
            'payment_count': 0
        }
    
    # Get last 4 payments to show recent pattern
    recent_payments = payments.head(4)
    
    payment_list = []
    for _, payment in recent_payments.iterrows():
        payment_list.append({
            'date': payment['date'].strftime('%Y-%m-%d'),
            'amount': abs(payment['amount']),
            'description': payment['description']
        })
    
    return {
        'recent_payments': payment_list,
        'total_recent_payments': abs(recent_payments['amount'].sum()),
        'payment_count': len(recent_payments)
    }

def calculate_current_balance_split(table_name, person1_percentage=50, person1_name="Person 1", person2_name="Person 2"):
    """
    Calculate how the current total balance should be split between two people.
    This shows the total outstanding balance and each person's responsibility.
    
    Args:
        table_name: Database table name
        person1_percentage: Percentage for person 1 (0-100)
        person1_name: Name for person 1
        person2_name: Name for person 2
    
    Returns:
        Dictionary with current balance split calculations
    """
    with get_connection() as conn:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate total balance (sum of all transactions)
    # Positive amounts are charges, negative amounts are payments/credits
    total_balance = df['amount'].sum()
    
    # If balance is negative, it means there's a credit (overpayment)
    # If positive, it's the amount owed
    person1_share = total_balance * (person1_percentage / 100)
    person2_share = total_balance * ((100 - person1_percentage) / 100)
    
    # Get expenses only (positive amounts) for category breakdown
    expenses = df[df['amount'] > 0].copy()
    
    # Calculate by category
    category_splits = []
    for category in expenses['category'].unique():
        if pd.isna(category):
            continue
        category_expenses = expenses[expenses['category'] == category]['amount'].sum()
        person1_category = category_expenses * (person1_percentage / 100)
        person2_category = category_expenses * ((100 - person1_percentage) / 100)
        
        category_splits.append({
            'category': category,
            'total_amount': category_expenses,
            f'{person1_name}_share': person1_category,
            f'{person2_name}_share': person2_category
        })
    
    # Sort by total amount descending
    category_splits.sort(key=lambda x: x['total_amount'], reverse=True)
    
    return {
        'total_balance': total_balance,
        'total_expenses': expenses['amount'].sum() if len(expenses) > 0 else 0,
        'total_payments_credits': abs(df[df['amount'] < 0]['amount'].sum()) if len(df[df['amount'] < 0]) > 0 else 0,
        'person1_name': person1_name,
        'person2_name': person2_name,
        'person1_percentage': person1_percentage,
        'person2_percentage': 100 - person1_percentage,
        'person1_owes': person1_share,
        'person2_owes': person2_share,
        'category_breakdown': category_splits,
        'num_expense_transactions': len(expenses),
        'date_range': (df['date'].min().strftime('%Y-%m-%d'), df['date'].max().strftime('%Y-%m-%d')) if len(df) > 0 else ('N/A', 'N/A')
    }

def calculate_expense_split(table_name, person1_percentage=50, person1_name="Person 1", person2_name="Person 2"):
    """
    Calculate expense split between two people based on percentage split.
    Intelligently determines the period since last settlement payments.
    
    Args:
        table_name: Database table name
        person1_percentage: Percentage for person 1 (0-100)
        person1_name: Name for person 1
        person2_name: Name for person 2
    
    Returns:
        Dictionary with split calculations
    """
    with get_connection() as conn:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date', ascending=False)  # Most recent first
    
    # Find the last settlement date by looking for payment patterns
    last_settlement_date = find_last_settlement_date(df)
    
    # Get transactions since last settlement
    if last_settlement_date:
        recent = df[df['date'] > last_settlement_date]
        settlement_info = f"Since last settlement on {last_settlement_date.strftime('%Y-%m-%d')}"
    else:
        # Fallback to last 30 days if no settlement pattern found
        recent = df[df['date'] >= pd.Timestamp.now() - pd.Timedelta(days=30)]
        settlement_info = "Last 30 days (no settlement pattern detected)"
    
    # Filter out transfers and income (positive amounts)
    expenses = recent[recent['amount'] < 0].copy()  # Negative amounts are expenses
    
    total_expenses = abs(expenses['amount'].sum())
    person1_share = total_expenses * (person1_percentage / 100)
    person2_share = total_expenses * ((100 - person1_percentage) / 100)
    
    # Calculate by category
    category_splits = []
    for category in expenses['category'].unique():
        if pd.isna(category):
            continue
        category_expenses = abs(expenses[expenses['category'] == category]['amount'].sum())
        person1_category = category_expenses * (person1_percentage / 100)
        person2_category = category_expenses * ((100 - person1_percentage) / 100)
        
        category_splits.append({
            'category': category,
            'total_amount': category_expenses,
            f'{person1_name}_share': person1_category,
            f'{person2_name}_share': person2_category
        })
    
    # Sort by total amount descending
    category_splits.sort(key=lambda x: x['total_amount'], reverse=True)
    
    return {
        'total_expenses': total_expenses,
        'person1_name': person1_name,
        'person2_name': person2_name,
        'person1_percentage': person1_percentage,
        'person2_percentage': 100 - person1_percentage,
        'person1_share': person1_share,
        'person2_share': person2_share,
        'category_breakdown': category_splits,
        'num_expense_transactions': len(expenses),
        'settlement_info': settlement_info,
        'date_range': (expenses['date'].min().strftime('%Y-%m-%d'), expenses['date'].max().strftime('%Y-%m-%d')) if len(expenses) > 0 else ('N/A', 'N/A')
    }

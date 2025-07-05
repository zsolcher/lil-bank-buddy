"""
Bank account analysis functionality.

Provides classes and functions for analyzing bank transactions,
detecting settlement patterns, and calculating expense splits.
"""

from typing import Dict, List, Optional, Any
import pandas as pd
from .database import db_manager
from ..utils.formatters import format_dollar


class BankAnalyzer:
    """Handles analysis of bank account transactions."""
    
    def __init__(self, db_manager_instance=None):
        """
        Initialize the BankAnalyzer.
        
        Args:
            db_manager_instance: DatabaseManager instance (uses global if None)
        """
        self.db = db_manager_instance or db_manager
    
    def get_account_summary(self, table_name: str) -> Dict[str, Any]:
        """
        Get summary statistics for an account.
        
        Args:
            table_name: Name of the database table
            
        Returns:
            Dictionary containing account summary statistics
        """
        with self.db.get_connection() as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        # Import data quality utilities
        from ..utils.data_quality import get_realistic_date_range, analyze_date_quality
        
        # Convert date column to datetime for proper analysis
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Get realistic date range (excluding far-future scheduled transactions)
        min_date, max_date = get_realistic_date_range(df, include_near_future=False)
        
        # Analyze data quality for reporting
        date_quality = analyze_date_quality(df)
        
        summary = {
            'total_transactions': len(df),
            'total_amount': format_dollar(df['amount'].sum()),
            'largest_transaction': format_dollar(df['amount'].max()),
            'smallest_transaction': format_dollar(df['amount'].min()),
            'date_range': (min_date, max_date),
            'most_frequent_category': df['category'].mode()[0] if not df['category'].isnull().all() else None,
            'data_quality': date_quality,  # Include data quality info for debugging
        }
        return summary
    
    def get_recent_activity(self, table_name: str, days: int = 30) -> Dict[str, Any]:
        """
        Get recent account activity.
        
        Args:
            table_name: Name of the database table
            days: Number of recent days to analyze
            
        Returns:
            Dictionary containing recent activity summary
        """
        with self.db.get_connection() as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        df['date'] = pd.to_datetime(df['date'])
        recent = df[df['date'] >= pd.Timestamp.now() - pd.Timedelta(days=days)]
        
        return {
            'num_transactions': len(recent),
            'total_amount': format_dollar(recent['amount'].sum()),
            'top_categories': recent['category'].value_counts().head(3).to_dict(),
        }
    
    def find_last_settlement_date(self, df: pd.DataFrame) -> Optional[pd.Timestamp]:
        """
        Find the last settlement date by analyzing payment patterns.
        
        Args:
            df: DataFrame with transaction data, sorted by date descending
            
        Returns:
            Last settlement date or None if no pattern found
        """
        # Look for credit card payments
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
    
    def analyze_payment_patterns(self, table_name: str) -> Dict[str, Any]:
        """
        Analyze payment patterns to identify individual contributors.
        
        Args:
            table_name: Name of the database table
            
        Returns:
            Dictionary with payment analysis
        """
        with self.db.get_connection() as conn:
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
    
    def validate_data_quality(self, table_name: str) -> Dict[str, Any]:
        """
        Check for data quality issues in the account data.
        
        Args:
            table_name: Name of the database table
            
        Returns:
            Dictionary containing data quality analysis
        """
        with self.db.get_connection() as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        # Convert dates and check for issues
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        today = pd.Timestamp.now()
        future_dates = df[df['date'] > today]
        null_dates = df[df['date'].isnull()]
        
        return {
            'total_rows': len(df),
            'future_dates_count': len(future_dates),
            'null_dates_count': len(null_dates),
            'future_dates': future_dates[['date', 'description', 'amount']].head(10).to_dict('records') if len(future_dates) > 0 else [],
            'date_range_valid': (df['date'].min().strftime('%Y-%m-%d'), df['date'].max().strftime('%Y-%m-%d')) if len(df) > 0 else ('N/A', 'N/A')
        }
    


class ExpenseSplitter:
    """Handles expense splitting calculations between multiple people."""
    
    def __init__(self, db_manager_instance=None):
        """
        Initialize the ExpenseSplitter.
        
        Args:
            db_manager_instance: DatabaseManager instance (uses global if None)
        """
        self.db = db_manager_instance or db_manager
        self.analyzer = BankAnalyzer(db_manager_instance)
    
    def calculate_current_balance_split(
        self, 
        table_name: str, 
        person1_percentage: int = 50, 
        person1_name: str = "Person 1", 
        person2_name: str = "Person 2"
    ) -> Dict[str, Any]:
        """
        Calculate how the current total balance should be split between two people.
        
        Args:
            table_name: Database table name
            person1_percentage: Percentage for person 1 (0-100)
            person1_name: Name for person 1
            person2_name: Name for person 2
            
        Returns:
            Dictionary with current balance split calculations
        """
        with self.db.get_connection() as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        df['date'] = pd.to_datetime(df['date'])
        
        # Calculate total balance (sum of all transactions)
        total_balance = df['amount'].sum()
        
        # Calculate split
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
    
    def calculate_expense_split(
        self, 
        table_name: str, 
        person1_percentage: int = 50, 
        person1_name: str = "Person 1", 
        person2_name: str = "Person 2"
    ) -> Dict[str, Any]:
        """
        Calculate expense split since last settlement.
        
        Args:
            table_name: Database table name
            person1_percentage: Percentage for person 1 (0-100)
            person1_name: Name for person 1
            person2_name: Name for person 2
            
        Returns:
            Dictionary with split calculations
        """
        with self.db.get_connection() as conn:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date', ascending=False)
        
        # Find the last settlement date
        last_settlement_date = self.analyzer.find_last_settlement_date(df)
        
        # Get transactions since last settlement
        if last_settlement_date:
            recent = df[df['date'] > last_settlement_date]
            settlement_info = f"Since last settlement on {last_settlement_date.strftime('%Y-%m-%d')}"
        else:
            # Fallback to last 30 days if no settlement pattern found
            recent = df[df['date'] >= pd.Timestamp.now() - pd.Timedelta(days=30)]
            settlement_info = "Last 30 days (no settlement pattern detected)"
        
        # Filter out transfers and income (positive amounts)
        expenses = recent[recent['amount'] < 0].copy()
        
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


# Legacy functions for backward compatibility
def get_account_summary(table_name: str) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    analyzer = BankAnalyzer()
    return analyzer.get_account_summary(table_name)


def get_recent_activity(table_name: str, days: int = 30) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    analyzer = BankAnalyzer()
    return analyzer.get_recent_activity(table_name, days)


def analyze_payment_patterns(table_name: str) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    analyzer = BankAnalyzer()
    return analyzer.analyze_payment_patterns(table_name)


def calculate_current_balance_split(
    table_name: str, 
    person1_percentage: int = 50, 
    person1_name: str = "Person 1", 
    person2_name: str = "Person 2"
) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    splitter = ExpenseSplitter()
    return splitter.calculate_current_balance_split(table_name, person1_percentage, person1_name, person2_name)


def calculate_expense_split(
    table_name: str, 
    person1_percentage: int = 50, 
    person1_name: str = "Person 1", 
    person2_name: str = "Person 2"
) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    splitter = ExpenseSplitter()
    return splitter.calculate_expense_split(table_name, person1_percentage, person1_name, person2_name)

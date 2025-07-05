"""Data quality utilities for identifying and handling data issues."""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

def analyze_date_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze date quality in a transaction DataFrame.
    
    Args:
        df: DataFrame with 'date' column
        
    Returns:
        Dictionary with date quality analysis
    """
    # Convert to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    today = pd.Timestamp.now()
    future_cutoff = today + timedelta(days=7)  # Allow up to 1 week in future for pending transactions
    
    # Categorize transactions
    historical = df[df['date'] <= today]
    near_future = df[(df['date'] > today) & (df['date'] <= future_cutoff)]
    far_future = df[df['date'] > future_cutoff]
    invalid_dates = df[df['date'].isnull()]
    
    return {
        'total_transactions': len(df),
        'historical_count': len(historical),
        'near_future_count': len(near_future),
        'far_future_count': len(far_future),
        'invalid_dates_count': len(invalid_dates),
        'far_future_transactions': far_future[['date', 'description', 'amount']].head(5).to_dict('records') if len(far_future) > 0 else [],
        'date_range_all': (df['date'].min(), df['date'].max()),
        'date_range_historical': (historical['date'].min(), historical['date'].max()) if len(historical) > 0 else (None, None),
    }

def get_realistic_date_range(df: pd.DataFrame, include_near_future: bool = True) -> Tuple[str, str]:
    """
    Get a realistic date range excluding far-future scheduled transactions.
    
    Args:
        df: DataFrame with 'date' column
        include_near_future: Whether to include transactions within 1 week of today
        
    Returns:
        Tuple of (min_date, max_date) as formatted strings
    """
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    today = pd.Timestamp.now()
    if include_near_future:
        future_cutoff = today + timedelta(days=7)
        filtered_df = df[df['date'] <= future_cutoff]
    else:
        filtered_df = df[df['date'] <= today]
    
    if len(filtered_df) == 0:
        return ('N/A', 'N/A')
    
    min_date = filtered_df['date'].min().strftime('%Y-%m-%d')
    max_date = filtered_df['date'].max().strftime('%Y-%m-%d')
    
    return (min_date, max_date)

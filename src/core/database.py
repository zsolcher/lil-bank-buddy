"""
Database management utilities for lil-bank-buddy.

Provides a centralized database manager class for handling SQLite operations.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, List, Optional, Tuple


class DatabaseManager:
    """Manages database connections and operations for bank transaction data."""
    
    def __init__(self, db_path: str = 'data/usaa_transactions.db'):
        """
        Initialize the DatabaseManager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self._ensure_data_directory()
    
    def _ensure_data_directory(self) -> None:
        """Ensure the data directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Get a database connection with automatic cleanup.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> sqlite3.Cursor:
        """
        Execute a query that modifies the database.
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            
        Returns:
            sqlite3.Cursor: Cursor object
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params or ())
            conn.commit()
            return cur
    
    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Tuple[Any, ...]]:
        """
        Fetch all results from a SELECT query.
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            
        Returns:
            List of tuples containing query results
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params or ())
            return cur.fetchall()
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.fetch_all(query, (table_name,))
        return len(result) > 0
    
    def import_dataframe(self, df, table_name: str, if_exists: str = 'append') -> int:
        """
        Import a pandas DataFrame into a database table.
        
        Args:
            df: pandas DataFrame to import
            table_name: Name of the target table
            if_exists: What to do if table exists ('append', 'replace', 'fail')
            
        Returns:
            Number of rows imported
        """
        with self.get_connection() as conn:
            rows_imported = len(df)
            df.to_sql(table_name, conn, if_exists=if_exists, index=False)
            return rows_imported


# Global instance for backward compatibility
db_manager = DatabaseManager()


@contextmanager 
def get_connection():
    """Legacy function for backward compatibility."""
    with db_manager.get_connection() as conn:
        yield conn


def execute_query(query: str, params: Optional[Tuple] = None) -> sqlite3.Cursor:
    """Legacy function for backward compatibility."""
    return db_manager.execute_query(query, params)


def fetch_all(query: str, params: Optional[Tuple] = None) -> List[Tuple[Any, ...]]:
    """Legacy function for backward compatibility."""
    return db_manager.fetch_all(query, params)

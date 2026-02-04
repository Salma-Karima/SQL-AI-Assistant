import sqlite3
from sqlalchemy import create_engine, inspect
import pandas as pd
import threading

class DatabaseConnector:
    def __init__(self, db_path='data/sample_sales.db'):
        self.db_path = db_path
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            connect_args={'check_same_thread': False}  # ✅ Fix threading issue
        )
        self._local = threading.local()
    
    def _get_connection(self):
        """Get thread-local connection"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self._local.conn
    
    def get_schema(self):
        """Extract database schema for LLM context"""
        inspector = inspect(self.engine)
        schema_info = []
        
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            schema_info.append(f"\n📋 Table: {table_name}")
            
            for col in columns:
                schema_info.append(
                    f"  - {col['name']} ({col['type']})"
                )
            
            # Get foreign keys
            fks = inspector.get_foreign_keys(table_name)
            if fks:
                schema_info.append("  Foreign Keys:")
                for fk in fks:
                    schema_info.append(
                        f"    - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}"
                    )
        
        return "\n".join(schema_info)
    
    def execute_query(self, query):
        """Execute SQL query and return results as DataFrame"""
        try:
            # Use thread-local connection
            conn = self._get_connection()
            df = pd.read_sql_query(query, conn)
            return df, None
        except Exception as e:
            return None, str(e)
    
    def get_sample_data(self, table_name, limit=3):
        """Get sample rows from a table"""
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        df, error = self.execute_query(query)
        return df if error is None else None
    
    def close(self):
        """Close all connections"""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
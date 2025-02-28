#!/usr/bin/env python3

import os
from typing import Optional
import psycopg2
from psycopg2.extensions import connection
from contextlib import contextmanager

class DatabaseConnector:
    """Manages database connections and operations for Market Lens."""
    
    def __init__(self):
        self.db_name = "market_lens"
        self.host = "localhost"
        self.port = 5432
        self.user = os.getenv("DB_USER", "")  # Get from environment variable
        self.password = os.getenv("DB_PASSWORD", "")  # Get from environment variable
        
    @contextmanager
    def get_connection(self) -> connection:
        """Get a database connection using context manager."""
        conn = None
        try:
            conn = psycopg2.connect(
                dbname=self.db_name,
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            yield conn
        finally:
            if conn is not None:
                conn.close()
                
    def execute_query(self, query: str, params: tuple = None) -> Optional[list]:
        """Execute a query and return results if any."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if cur.description:  # If query returns data
                    return cur.fetchall()
                conn.commit()
                return None
                
    def execute_many(self, query: str, params_list: list[tuple]) -> None:
        """Execute a query with multiple parameter sets."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(query, params_list)
                conn.commit()

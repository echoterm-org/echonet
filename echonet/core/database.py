import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


class SqliteDB:
    """
    Lightweight SQLite database helper class with connection reuse.

    Features:
        - Persistent connection for better performance
        - Safe parameter binding (avoids SQL injection)
        - Dict-like result rows (sqlite3.Row)
        - Context manager support
    """

    def __init__(self, db_path: str | Path, init_script: str | None = None) -> None:
        """
        Args:
            db_path: Path to SQLite database file. Use ':memory:' for in-memory DB.
        """
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row

        if init_script:
            self.execute(init_script, commit=True)

    def __enter__(self) -> "SqliteDB":
        """Allows use in `with` statements."""
        return self

    def __exit__(self) -> None:
        """Closes the DB connection on exit."""
        self.close()

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def execute(
        self,
        query: str,
        params: tuple = (),
        commit: bool = False,
        fetchone: bool = False,
        fetchall: bool = False,
        as_dict: bool = False,
    ) -> Any | list[Any] | None:
        """
        Execute a SQL query with optional commit and fetch options.

        Args:
            query: SQL statement (use `?` placeholders for parameters).
            params: Parameters bound to the SQL query.
            commit: If True, commit the transaction.
            fetchone: If True, fetch a single row.
            fetchall: If True, fetch all rows.
            as_dict: If True, return results as plain dict(s) instead of sqlite3.Row.

        Returns:
            One row, list of rows, or None.
        """
        with closing(self._conn.cursor()) as cur:
            cur.execute(query, params)
            if commit:
                self._conn.commit()

            if fetchone:
                row = cur.fetchone()
                return dict(row) if as_dict else row

            if fetchall:
                rows = cur.fetchall()
                return [dict(row) for row in rows] if as_dict else rows

    def insert(self, query: str, params: tuple = ()) -> None:
        """Execute INSERT/UPDATE/DELETE."""
        self.execute(query, params, commit=True)

    def select_one(self, query: str, params: tuple = ()) -> Any:
        """Fetch a single row for a SELECT query."""
        return self.execute(query, params, fetchone=True, as_dict=True)

    def select_all(self, query: str, params: tuple = ()) -> list[Any] | None:
        """Fetch all rows for a SELECT query."""
        return self.execute(query, params, fetchall=True, as_dict=True)

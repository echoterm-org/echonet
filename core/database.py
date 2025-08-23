import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


class SqliteDB:
    """
    Lightweight SQLite database helper class.

    This class wraps Python's built-in `sqlite3` module to simplify
    CRUD operations by providing:
      - Automatic connection management
      - Safe parameter binding (avoiding SQL injection)
      - Row objects as dict-like `sqlite3.Row`
      - Convenience methods (`insert`, `select_all`, `select_one`)

    Example:
    ```py
        db = SqliteDB("example.db")
        db.insert("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        db.insert("INSERT INTO users (name) VALUES (?)", ("Alice",))
        rows = db.select_all("SELECT * FROM users")
        for row in rows:
            print(dict(row))
    ```
    """

    def __init__(self, db_path: str | Path) -> None:
        """
        Initialize the database helper.

        Args:
            db_path (str): Path to the SQLite database file. Use ':memory:' for
                           an in‑memory database.
        """
        self._path = db_path

    def execute(
        self,
        query: str,
        params: tuple = (),
        commit: bool = False,
        fetchone: bool = False,
        fetchall: bool = False,
    ) -> Any | list[Any] | None:
        """
        Execute a SQL query with optional commit and fetch options.

        Args:
            query (str): The SQL statement to execute (use `?` placeholders for parameters).
            params (tuple, optional): Parameters bound to the SQL query. Defaults to ().
            commit (bool, optional): Whether to commit the transaction. Needed for INSERT/UPDATE/DELETE.
            fetchone (bool, optional): If True, fetch a single row from results.
            fetchall (bool, optional): If True, fetch all rows from results.

        Returns:
            Any | list[Any] | None: Result row(s) if `fetchone` or `fetchall` is set,
                                    otherwise None.

        Notes:
            - Automatically enables `sqlite3.Row` for dict-style row access.
            - Use only one of `fetchone` or `fetchall` per call for clarity.
        """
        with sqlite3.connect(self._path) as conn:
            conn.row_factory = sqlite3.Row  # enables dict-like column access
            with closing(conn.cursor()) as cur:
                cur.execute(query, params)

                # Commit if explicitly requested
                if commit:
                    conn.commit()

                # Fetch results if required
                if fetchone:
                    return cur.fetchone()
                if fetchall:
                    return cur.fetchall()

    def insert(self, query: str, params: tuple = ()) -> None:
        """
        Execute an INSERT/UPDATE/DELETE type query with commit.

        Args:
            query (str): SQL statement with placeholders (`?`).
            params (tuple): Parameter values.
        """
        self.execute(query, params, commit=True)

    def select_all(self, query: str, params: tuple = ()) -> list[Any] | None:
        """
        Fetch all rows matching a SELECT query.

        Args:
            query (str): SQL SELECT statement.
            params (tuple): Parameter values.

        Returns:
            list[Any] | None: List of `sqlite3.Row` objects.
        """
        return self.execute(query, params, fetchall=True)

    def select_one(self, query: str, params: tuple = ()) -> Any:
        """
        Fetch a single row matching a SELECT query.

        Args:
            query (str): SQL SELECT statement.
            params (tuple): Parameter values.

        Returns:
            Any: A single `sqlite3.Row` object, or None if no match.
        """
        return self.execute(query, params, fetchone=True)

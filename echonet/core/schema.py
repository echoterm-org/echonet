SQL_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dns_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dns_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    primary_ip TEXT NOT NULL CHECK (primary_ip != ''),
    secondary_ip TEXT,
    description TEXT,
    tags TEXT,
    FOREIGN KEY (list_id) REFERENCES dns_lists (id) ON DELETE CASCADE
);
"""

from pathlib import Path

from appdirs import user_data_dir, user_log_dir

APP_NAME = "EchoNet"
APP_AUTHOR = "EchoTerm"

# --- Base directories ---
LOG_DIR = Path(user_log_dir(appname=APP_NAME, appauthor=APP_AUTHOR))
DATA_DIR = Path(user_data_dir(appname=APP_NAME, appauthor=APP_AUTHOR))

# Ensure directories exist
for directory in (LOG_DIR, DATA_DIR):
    directory.mkdir(parents=True, exist_ok=True)

# --- File paths ---
# Core files
LOG_FILE = LOG_DIR / "echonet.log"

# Data Files
DB_FILE = DATA_DIR / "database.db"

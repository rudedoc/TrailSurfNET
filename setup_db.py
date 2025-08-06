#!/usr/bin/env python
# reset_and_import_osm.py

import os
import subprocess
import sys
import shutil  # NEW: Import for checking command existence
import requests
from sqlalchemy import create_engine, text
import getpass

# --- Configuration ---
DB_NAME = "osm"
# Assumes the user running the script has permissions to create databases.
# You might want to hardcode this to 'postgres' if that's your admin user.
DB_USER = getpass.getuser()
DB_HOST = "localhost"
DB_PORT = "5432"

# OSM data files from Geofabrik.
# Note: Geofabrik's 'ireland-and-northern-ireland' extract includes Northern Ireland.
# The 'united-kingdom' extract contains only Great Britain (England, Scotland, Wales).
# This prevents data duplication for Northern Ireland.
FILE_IRELAND = "ireland-and-northern-ireland-latest.osm.pbf"
FILE_UK = "great-britain-latest.osm.pbf" # Renamed for clarity based on Geofabrik content

# --- Step 0: Prerequisite Checks ---
def check_prerequisites():
    """Checks if required command-line tools are installed and in the PATH."""
    print("--- Running Prerequisite Checks ---")
    # A dictionary of required command-line tools and suggestions for installation.
    required_tools = {
        "psql": "Please install the postgresql-client package (e.g., 'sudo apt install postgresql-client').",
        "osm2pgsql": "Please install osm2pgsql (e.g., 'sudo apt install osm2pgsql')."
    }
    all_found = True

    for tool, suggestion in required_tools.items():
        # shutil.which() is the modern, cross-platform way to find an executable.
        if shutil.which(tool) is None:
            print(f"❌ ERROR: Command '{tool}' not found in your system's PATH.")
            print(f"   Suggestion: {suggestion}")
            all_found = False
        else:
            print(f"✅ Found '{tool}' at: {shutil.which(tool)}")

    if not all_found:
        print("\n❌ One or more required tools are missing. Halting script.")
        # Exit the script with an error code to prevent further execution.
        sys.exit(1)
    else:
        print("--- All prerequisites met. Proceeding with script. ---\n")

# Run the checks before doing anything else.
check_prerequisites()

# --- Step 1: Reset the Database ---

# Connect to the default 'postgres' database to manage the target DB.
try:
    engine_postgres = create_engine(f"postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/postgres", connect_args={'connect_timeout': 5})
    # Use autocommit mode because DROP DATABASE cannot run inside a transaction.
    with engine_postgres.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        print(f"Dropping database '{DB_NAME}' (if it exists)...")
        conn.execute(text(f"DROP DATABASE IF EXISTS {DB_NAME};"))

        print(f"Creating fresh database '{DB_NAME}'...")
        conn.execute(text(f"CREATE DATABASE {DB_NAME};"))
except Exception as e:
    print(f"❌ ERROR: Could not connect to PostgreSQL or reset the database.")
    print(f"   Please ensure PostgreSQL is running and user '{DB_USER}' has the necessary permissions.")
    print(f"   Details: {e}")
    sys.exit(1)


# Now, connect to the newly created database.
engine_osm = create_engine(f"postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Again, use autocommit for extension creation
with engine_osm.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    print("Enabling PostGIS and hstore extensions...")
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS hstore;"))

print(f"✅ Database '{DB_NAME}' has been reset and extensions enabled.")

# --- Step 2: Download OSM Extracts if Not Present ---
def download_file(url, filename):
    print(f"Downloading {filename}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ {filename} downloaded successfully.")
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Failed to download {filename}.")
        print(f"   Details: {e}")
        sys.exit(1)

# Geofabrik's Europe directory contains both extracts
base_url = "https://download.geofabrik.de/europe/"

if not os.path.isfile(FILE_IRELAND):
    download_file(base_url + FILE_IRELAND, FILE_IRELAND)
else:
    print(f"'{FILE_IRELAND}' already exists, skipping download.")

# Note: Changed from 'united-kingdom' to 'great-britain' to match Geofabrik naming
# and avoid confusion about Northern Ireland.
if not os.path.isfile(FILE_UK):
    download_file(base_url + "great-britain-latest.osm.pbf", FILE_UK)
else:
    print(f"'{FILE_UK}' already exists, skipping download.")

# --- Step 3: Import OSM Data using osm2pgsql ---
# Adjust cache based on your machine's available RAM. 8000MB is a good start for a 16GB machine.
osm2pgsql_command = [
    "osm2pgsql",
    "--create",
    "--slim",
    "--extra-attributes",
    "--hstore",
    "--hstore-add-index",
    "-d", DB_NAME,
    "--cache", "8000",
    FILE_UK,
    FILE_IRELAND
]

print("\nImporting OSM data using osm2pgsql... This may take a long time.")
print(f"Running command: {' '.join(osm2pgsql_command)}")
try:
    # Use check=True to automatically raise an exception if osm2pgsql returns a non-zero exit code
    subprocess.run(osm2pgsql_command, check=True)
    print("✅ OSM data imported successfully.")
except FileNotFoundError:
    # This is a fallback check in case shutil.which was wrong, but it's good practice
    print(f"❌ ERROR: Command 'osm2pgsql' not found. Please ensure it is installed and in your PATH.")
    sys.exit(1)
except subprocess.CalledProcessError as e:
    print(f"❌ ERROR: osm2pgsql failed with exit code {e.returncode}.")
    print("   Check the output above for details from osm2pgsql.")
    sys.exit(1)

print("\n🎉 Script finished successfully!")
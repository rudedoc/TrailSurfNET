#!/usr/bin/env python
# reset_and_import_osm.py

import os
import subprocess
import requests
from sqlalchemy import create_engine, text

# --- Configuration ---
DB_NAME = "osm"
DB_USER = "markfinlay"
DB_HOST = "localhost"
DB_PORT = "5432"

FILE_IRELAND = "ireland-and-northern-ireland-latest.osm.pbf"
FILE_UK = "united-kingdom-latest.osm.pbf"

# --- Step 1: Reset the Database ---

# Connect to the default 'postgres' database to manage the target DB.
engine_postgres = create_engine(f"postgresql://{DB_USER}:@{DB_HOST}:{DB_PORT}/postgres")

# Use autocommit mode because DROP DATABASE cannot run inside a transaction.
with engine_postgres.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    print(f"Dropping database {DB_NAME} (if it exists)...")
    conn.execute(text(f"DROP DATABASE IF EXISTS {DB_NAME};"))

    print(f"Creating fresh database {DB_NAME}...")
    conn.execute(text(f"CREATE DATABASE {DB_NAME};"))

# Now, connect to the newly created database.
engine_osm = create_engine(f"postgresql://{DB_USER}:@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Again, use autocommit for extension creation (optional, but can help avoid transactional issues)
with engine_osm.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    print("Enabling PostGIS and hstore extensions...")
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS hstore;"))

print(f"Database {DB_NAME} has been reset and extensions enabled.")

# --- Step 2: Download OSM Extracts if Not Present ---
def download_file(url, filename):
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"{filename} downloaded.")

base_url = "https://download.geofabrik.de/europe/"

if not os.path.isfile(FILE_IRELAND):
    download_file(base_url + FILE_IRELAND, FILE_IRELAND)
else:
    print(f"{FILE_IRELAND} already exists, skipping download.")

if not os.path.isfile(FILE_UK):
    download_file(base_url + FILE_UK, FILE_UK)
else:
    print(f"{FILE_UK} already exists, skipping download.")

# --- Step 3: Import OSM Data using osm2pgsql ---
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

print("Importing OSM data using osm2pgsql...")
try:
    subprocess.run(osm2pgsql_command, check=True)
    print("OSM data imported successfully.")
except subprocess.CalledProcessError as e:
    print("Error importing OSM data:", e)

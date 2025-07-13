#!/usr/bin/env python
# db_checker.py

import sqlalchemy
from sqlalchemy import create_engine, text, inspect

# --- Configuration ---
# Ensure these match your setup_db.py and other scripts
DB_NAME = "osm"
DB_USER = "markfinlay"
DB_HOST = "localhost"
DB_PORT = "5432"
# Add password if your DB user 'markfinlay' has one:
# DB_PASSWORD = "your_password"
# engine_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine_url = f"postgresql://{DB_USER}:@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_table_row_count(engine, table_name, schema='public'):
    """Counts the number of rows in a given table."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT COUNT(*) FROM {schema}.{table_name};"))
            count = result.scalar_one_or_none()
            return count
    except sqlalchemy.exc.ProgrammingError as e:
        if "relation" in str(e) and "does not exist" in str(e):
            print(f"Info: Table '{schema}.{table_name}' does not exist yet.")
            return None
        else:
            print(f"Error counting rows in {table_name}: {e}")
            return None
    except Exception as e:
        print(f"An unexpected error occurred while counting rows in {table_name}: {e}")
        return None

def get_column_counts(engine, table_name, column_name, schema='public'):
    """Gets counts for each unique value in a specified column."""
    counts = {}
    try:
        with engine.connect() as connection:
            query = text(f"SELECT {column_name}, COUNT(*) as count FROM {schema}.{table_name} GROUP BY {column_name} ORDER BY count DESC;")
            result = connection.execute(query)
            for row in result:
                counts[row[0]] = row[1]
            return counts
    except sqlalchemy.exc.ProgrammingError as e:
        if "relation" in str(e) and "does not exist" in str(e):
            print(f"Info: Table '{schema}.{table_name}' for column counts does not exist yet.")
            return None
        elif "column" in str(e) and "does not exist" in str(e):
            print(f"Info: Column '{column_name}' in table '{schema}.{table_name}' does not exist yet.")
            return None
        else:
            print(f"Error getting column counts for {table_name}.{column_name}: {e}")
            return None
    except Exception as e:
        print(f"An unexpected error occurred while getting column counts for {table_name}.{column_name}: {e}")
        return None

def check_column_exists(engine, table_name, column_name, schema='public'):
    """Checks if a column exists in a table."""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name, schema=schema)]
        return column_name in columns
    except sqlalchemy.exc.NoSuchTableError:
        print(f"Info: Table '{schema}.{table_name}' for column check does not exist yet.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while checking column {column_name} in {table_name}: {e}")
        return False

def main():
    print(f"Connecting to database: {DB_NAME} on {DB_HOST}:{DB_PORT} as user {DB_USER}")
    try:
        engine = create_engine(engine_url)
        with engine.connect() as connection: # Test connection
            print("Successfully connected to the database.\n")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        return

    print("--- OSM2PGSQL Standard Table Counts ---")
    osm_tables = ["planet_osm_point", "planet_osm_line", "planet_osm_polygon", "planet_osm_roads"]
    for table in osm_tables:
        count = get_table_row_count(engine, table)
        if count is not None:
            print(f"Rows in {table}: {count:,}")
    print("-" * 30)

    print("\n--- planet_osm_line Processing Checks ---")
    # Check for surface_group column
    pol_table = "planet_osm_line"
    sg_column = "surface_group"
    if check_column_exists(engine, pol_table, sg_column):
        print(f"Column '{sg_column}' exists in '{pol_table}'.")
        surface_group_counts = get_column_counts(engine, pol_table, sg_column)
        if surface_group_counts is not None:
            if surface_group_counts:
                print(f"Counts per '{sg_column}' in '{pol_table}':")
                for group, num in surface_group_counts.items():
                    print(f"  - {group if group is not None else 'NULL'}: {num:,}")
            else:
                print(f"No data found for '{sg_column}' counts in '{pol_table}', or column is all NULLs after grouping.")
    else:
        print(f"Column '{sg_column}' does NOT exist in '{pol_table}' (or table itself doesn't exist). This is expected if OSM Data.py hasn't run its ALTER TABLE step.")
    print("-" * 30)


    print("\n--- Custom Processed Table Checks ---")
    custom_tables = {
        "balanced_planet_osm_line": "surface_group",
        "trail_segments": "surface_group"
    }

    for table, group_col in custom_tables.items():
        count = get_table_row_count(engine, table)
        if count is not None:
            print(f"Rows in {table}: {count:,}")
            if check_column_exists(engine, table, group_col):
                col_counts = get_column_counts(engine, table, group_col)
                if col_counts is not None:
                    if col_counts:
                        print(f"  Counts per '{group_col}' in '{table}':")
                        for group_val, num in col_counts.items():
                            print(f"    - {group_val if group_val is not None else 'NULL'}: {num:,}")
                    else:
                        print(f"  No data found for '{group_col}' counts in '{table}'.")
            else:
                print(f"  Column '{group_col}' does NOT exist in '{table}'.")

            if table == "trail_segments":
                id_column = "image_data"
                if check_column_exists(engine, table, id_column):
                    print(f"  Column '{id_column}' exists in '{table}'.")
                    with engine.connect() as connection:
                        try:
                            result = connection.execute(text(f"SELECT COUNT(*) FROM {table} WHERE {id_column} IS NOT NULL;"))
                            img_data_count = result.scalar_one()
                            print(f"  Segments with non-NULL '{id_column}': {img_data_count:,}")
                            result = connection.execute(text(f"SELECT COUNT(*) FROM {table} WHERE {id_column} IS NULL;"))
                            null_img_data_count = result.scalar_one()
                            print(f"  Segments with NULL '{id_column}': {null_img_data_count:,}")
                        except Exception as e:
                            print(f"  Error checking '{id_column}' in '{table}': {e}")

                else:
                    print(f"  Column '{id_column}' does NOT exist in '{table}'.")
        print("-" * 15)
    print("-" * 30)

    print("\nDatabase checks complete.")

if __name__ == "__main__":
    main()

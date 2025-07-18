from db_utils import backfill_properties_to_normalized_tables

if __name__ == "__main__":
    print("Starting backfill of normalized tables from existing properties...")
    backfill_properties_to_normalized_tables()
    print("Backfill complete.") 
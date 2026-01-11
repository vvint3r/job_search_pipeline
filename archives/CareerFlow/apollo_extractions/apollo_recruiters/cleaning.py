import pandas as pd
import os

def remove_duplicates_from_csv():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Read the input CSV file
    input_file = 'apollo_recruiter_records.csv'
    input_path = os.path.join(script_dir, input_file)
    df = pd.read_csv(input_path)
    
    # Get the number of records before deduplication
    records_before = len(df)
    
    # Remove duplicates and keep the first occurrence
    df_deduplicated = df.drop_duplicates()
    
    # Get the number of records after deduplication
    records_after = len(df_deduplicated)
    
    # Create output filename
    base_name = os.path.splitext(input_file)[0]
    output_file = os.path.join(script_dir, f"{base_name}_deduplicated.csv")
    
    # Save the deduplicated data
    df_deduplicated.to_csv(output_file, index=False)
    
    print(f"Original records: {records_before}")
    print(f"Records after deduplication: {records_after}")
    print(f"Removed {records_before - records_after} duplicate records")
    print(f"Deduplicated data saved to: {output_file}")

if __name__ == "__main__":
    remove_duplicates_from_csv()

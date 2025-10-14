import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import argparse
import os

# --- Configuration ---
# NOTE: You need to create a service account and download its JSON key file.
# See the gspread documentation for more details: https://docs.gspread.org/en/latest/oauth2.html
SCOPE = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']
# The name of the Google Sheet
SHEET_NAME = 'GenX_FX_Master_Credentials'


def get_sheet_data(service_account_file):
    """Connects to the Google Sheet and returns the data as a pandas DataFrame."""
    if not os.path.exists(service_account_file):
        print(f"Error: Service account file not found at '{service_account_file}'")
        print("Please provide a valid path using the --creds-file argument.")
        return None

    try:
        creds = Credentials.from_service_account_file(service_account_file, scopes=SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        print(f"An error occurred while connecting to the Google Sheet: {e}")
        return None


def analyze_duplicates(df):
    """Finds and counts duplicates in each column."""
    print("\n--- Duplicate Analysis ---")
    for column in df.columns:
        duplicates = df[column].duplicated().sum()
        print(f"Column '{column}': {duplicates} duplicates")


def analyze_blank_cells(df):
    """Finds and counts blank cells in each column."""
    print("\n--- Blank Cell Analysis ---")
    for column in df.columns:
        # Consider empty strings as blank cells as well
        blank_cells = (df[column].isnull() | (df[column] == '')).sum()
        print(f"Column '{column}': {blank_cells} blank cells")


def analyze_value_variations(df):
    """Identifies and lists variations in values within each column."""
    print("\n--- Value Variation Analysis ---")
    for column in df.columns:
        print(f"\nColumn '{column}':")
        # Convert to lowercase and strip whitespace to find variations
        lower_stripped_series = df[column].astype(str).str.lower().str.strip()
        unique_variations = lower_stripped_series.value_counts()

        # Check for variations by comparing original values to normalized ones
        original_unique_values = df[column].dropna().unique()
        if len(original_unique_values) != len(unique_variations):
            print("  Variations found (case or whitespace differences):")
            for value, count in unique_variations.items():
                # Find original values that match the normalized value
                original_matches = [orig for orig in original_unique_values if str(orig).lower().strip() == value]
                if len(original_matches) > 1:
                     print(f"    - Normalized value '{value}' corresponds to: {original_matches}")

        else:
            print("  No significant variations found.")


def main():
    """Main function to run the analysis."""
    parser = argparse.ArgumentParser(description="Analyze a Google Sheet for data quality.")
    parser.add_argument(
        '--creds-file',
        type=str,
        default='credentials.json',
        help='Path to the service account credentials JSON file.'
    )
    args = parser.parse_args()

    df = get_sheet_data(args.creds_file)

    if df is not None:
        print(f"Successfully loaded {len(df)} rows from the sheet.")
        analyze_duplicates(df)
        analyze_blank_cells(df)
        analyze_value_variations(df)
    else:
        print("Could not retrieve data from the sheet. Exiting.")


if __name__ == "__main__":
    main()
